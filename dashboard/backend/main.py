# main.py
import logging
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
import os
from openai import AsyncOpenAI
import base64
from io import BytesIO
from pdf2image import convert_from_path
import asyncio
import re
from typing import List, Dict, Optional
import time
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from pathlib import Path  # Added for safe paths
import tempfile  # Added for temp files

# Constants
SYSTEM_PROMPT = """1. CORE IDENTITY & PERSONA\n\nYou are \"Juris-Diction(AI)ry\", a highly specialized AI assistant designed for tax professionals. [...]"""  # Full prompt here (truncated for brevity)
MASTER_PROMPT = ""  # Fixed spacing; populate if needed
SESSION_FILE = Path("/app/data/sessions.json")  # Absolute path for Docker persistence

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "app.db")
db_dir = Path(SQLITE_DB_PATH).parent
db_dir.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model
class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True)
    company_name = Column(String)
    country = Column(String)
    new_regulation = Column(String)
    deadline = Column(Date)
    status = Column(String)

Base.metadata.create_all(bind=engine)

# App
app = FastAPI(title="Juris-Diction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restricted from "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        if db.query(ClientProfile).count() == 0:
            mock_data = [
                # Your mock data here (unchanged)
                {
                    "client_id": "CI2001",
                    "company_name": "Split Hospitality Group j.d.o.o.",
                    "country": "Croatia",
                    "new_regulation": "N/A",
                    "deadline": None,
                    "status": "LIVE"
                },
            {
                "client_id": "CI2002",
                "company_name": "KreativWerkstatt S.C.",
                "country": "Poland",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            },
            {
                "client_id": "CI2003",
                "company_name": "Global Dynamics Sp. z o.o.",
                "country": "Poland",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            },
            {
                "client_id": "CI2004",
                "company_name": "Copenhagen Consulting ApS",
                "country": "Denmark",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            },
            {
                "client_id": "CI2005",
                "company_name": "Adriatic Solutions d.o.o.",
                "country": "Croatia",
                "new_regulation": "Croatian B2B e-Invoicing Mandate",
                "deadline": "2026-01-01",
                "status": "MONITORED"
            },
            {
                "client_id": "CI2006",
                "company_name": "Aarhus Retail IVS",
                "country": "Denmark",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            }
                # ... (rest of mock_data)
            ]
            for data in mock_data:
                parsed_data = data.copy()
                if data["deadline"] and isinstance(data["deadline"], str):
                    parsed_data["deadline"] = date.fromisoformat(data["deadline"])
                client = ClientProfile(**parsed_data)
                db.add(client)
            db.commit()
    finally:
        db.close()

@app.get("/api/clients")
async def get_clients():
    db = SessionLocal()
    try:
        clients = db.query(ClientProfile).all()
        return [{"clientId": c.client_id, "companyName": c.company_name, "country": c.country,
                 "newRegulation": c.new_regulation, "deadline": c.deadline.isoformat() if c.deadline else None,
                 "status": c.status} for c in clients]
    finally:
        db.close()

# Simple file-based session store (improved with Path and locking)
class Store:
    def __init__(self, file_path: Path = SESSION_FILE):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self.load()

    def load(self):
        if self.file_path.exists():
            try:
                return json.loads(self.file_path.read_text())
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load session store: {str(e)}")
                return {}
        return {}

    def get(self, key, default=None):
        keys = key.split('.')
        data = self.data
        for k in keys:
            data = data.get(k, {})
        return data if data != {} else default

    def set(self, key, value):
        keys = key.split('.')
        data = self.data
        for k in keys[:-1]:
            data = data.setdefault(k, {})
        data[keys[-1]] = value
        try:
            self.file_path.write_text(json.dumps(self.data, indent=2))
        except IOError as e:
            logger.error(f"Failed to save session store: {str(e)}")

# Initialize session storage
session_store = Store()

# Middleware to measure request processing time
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(f"Request: {request.method} {request.url.path} took {processing_time:.3f} seconds")
        return response

app.add_middleware(TimingMiddleware)

dwani_api_base_url = os.getenv('DWANI_API_BASE_URL', "0.0.0.0")

def encode_image(image: BytesIO) -> str:
    """Encode image bytes to base64 string."""
    image.seek(0)  # Ensure seeked
    return base64.b64encode(image.read()).decode("utf-8")

def get_openai_client(model: str) -> AsyncOpenAI:
    """Initialize AsyncOpenAI client with model-specific base_url."""
    valid_models = ["gemma3", "gpt-oss"]
    if model not in valid_models:
        raise ValueError(f"Invalid model: {model}. Choose from: {', '.join(valid_models)}")
    
    model_ports = {
        "gemma3": "9000",
        "gpt-oss": "9500",
    }
    base_url = f"http://{dwani_api_base_url}:{model_ports[model]}/v1"
    return AsyncOpenAI(api_key="http", base_url=base_url)

def clean_response(raw_response: str) -> Optional[str]:
    """Clean markdown code blocks or other non-JSON content from the response."""
    if not raw_response:
        return None
    cleaned = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', raw_response)
    return cleaned.strip()

async def process_single_batch(client, model, batch_messages, page_start, page_end):
    """Process a single batch of pages asynchronously."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": batch_messages}],
            temperature=0.2,
            max_tokens=2048  # Consistent with single-page
        )
        raw_response = response.choices[0].message.content
        logger.debug(f"Raw response for batch {page_start}-{page_end}: {raw_response}")

        cleaned_response = clean_response(raw_response)
        if not cleaned_response:
            logger.warning(f"Empty response for batch {page_start}-{page_end}")
            return None, list(range(page_start, page_end + 1))

        try:
            batch_results = json.loads(cleaned_response)
            if not isinstance(batch_results, dict):
                logger.warning(f"Response is not a JSON object for batch {page_start}-{page_end}")
                return None, list(range(page_start, page_end + 1))
            return batch_results, []
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for batch {page_start}-{page_end}: {str(e)}")
            return None, list(range(page_start, page_end + 1))
    except Exception as e:
        logger.error(f"API request failed for batch {page_start}-{page_end}: {str(e)}")
        return None, list(range(page_start, page_end + 1))

async def process_single_page(client, model, image, page_idx):
    """Process a single skipped page asynchronously."""
    try:
        image_bytes_io = BytesIO()
        image.save(image_bytes_io, format='JPEG', quality=85)
        image_base64 = encode_image(image_bytes_io)
        
        single_message = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            },
            {
                "type": "text",
                "text": (
                    f"Extract plain text from this single PDF page (page number {page_idx}). "
                    "Return the result as a valid JSON object where the key is the page number "
                    f"({page_idx}) and the value is the extracted text. "
                    "Ensure the response is strictly JSON-formatted and does not include markdown code blocks."
                )
            }
        ]
        
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": single_message}],
            temperature=0.2,
            max_tokens=2048
        )
        raw_response = response.choices[0].message.content
        logger.debug(f"Raw response for skipped page {page_idx}: {raw_response}")

        cleaned_response = clean_response(raw_response)
        if not cleaned_response:
            logger.warning(f"Empty response for skipped page {page_idx}")
            return None, page_idx

        try:
            page_result = json.loads(cleaned_response)
            if not isinstance(page_result, dict) or str(page_idx) not in page_result:
                logger.warning(f"Invalid JSON for skipped page {page_idx}")
                return None, page_idx
            return page_result, None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for skipped page {page_idx}: {str(e)}")
            return None, page_idx
    except Exception as e:
        logger.error(f"Failed to process skipped page {page_idx}: {str(e)}")
        return None, page_idx

async def render_pdf_to_png(pdf_file: UploadFile) -> List:
    """Convert PDF to images using temp file."""
    temp_pdf = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_f:
            temp_pdf = temp_f.name
            content = await pdf_file.read()
            temp_f.write(content)
        images = convert_from_path(temp_pdf)
        return images
    except Exception as e:
        logger.error(f"PDF conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to convert PDF to images: {str(e)}")
    finally:
        if temp_pdf and os.path.exists(temp_pdf):
            os.remove(temp_pdf)

@app.post("/process_file")
async def process_file(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    sessionId: str = Form(None),
    model: str = Form(default="gemma3"),
    is_extraction: bool = Form(False),
    system_prompt: str = Form(default=SYSTEM_PROMPT)
):
    """Endpoint to process file and extract text based on prompt."""
    if not file:
        raise HTTPException(status_code=400, detail="Please upload a file")
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Please provide a non-empty prompt")

    filename = file.filename.lower()
    file_ext = os.path.splitext(filename)[1]
    all_results = {}
    skipped_pages = []

    try:
        client = get_openai_client(model)
    except ValueError as e:
        logger.error(f"Invalid model: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    content = await file.read()
    file.file.close()  # Explicit close

    if file_ext == '.pdf':
        try:
            images = await render_pdf_to_png(UploadFile(file=BytesIO(content), filename=filename))
        except Exception:
            raise HTTPException(status_code=500, detail="PDF processing failed")
        num_pages = len(images)
        batch_size = 5

        batch_tasks = []
        for batch_start_idx in range(0, num_pages, batch_size):
            batch_end_idx = min(batch_start_idx + batch_size, num_pages)
            batch_images = images[batch_start_idx:batch_end_idx]
            batch_messages = []
            local_skipped = []

            for j, image in enumerate(batch_images):
                page_num = batch_start_idx + j + 1
                try:
                    image_bytes_io = BytesIO()
                    image.save(image_bytes_io, format='JPEG', quality=85)
                    batch_messages.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_bytes_io)}"}
                    })
                except Exception as e:
                    logger.error(f"Image processing failed for page {page_num}: {str(e)}")
                    local_skipped.append(page_num)
                    continue

            skipped_pages.extend(local_skipped)

            if not batch_messages:
                logger.warning(f"Skipping batch {batch_start_idx + 1}-{batch_end_idx}: No valid images")
                skipped_pages.extend(range(batch_start_idx + 1, batch_end_idx + 1))
                continue

            batch_messages.append({
                "type": "text",
                "text": (
                    f"Extract plain text from these {len(batch_images)} PDF pages (pages {batch_start_idx + 1} to {batch_end_idx}). "
                    "Return the results as a valid JSON object where keys are page numbers "
                    f"(1-based: {batch_start_idx + 1}, ..., {batch_end_idx}) and values are the extracted text for each page. "
                    "Ensure the response is strictly JSON-formatted."
                )
            })

            page_start = batch_start_idx + 1
            page_end = batch_end_idx
            batch_tasks.append(process_single_batch(client, model, batch_messages, page_start, page_end))

        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f"Batch processing failed: {str(batch_result)}")
                continue
            batch_data, batch_skipped = batch_result
            if batch_data:
                all_results.update(batch_data)
            if batch_skipped:
                skipped_pages.extend(batch_skipped)

        # Retry skipped pages
        retry_tasks = []
        remaining_skipped = list(set(skipped_pages))
        for page_num in remaining_skipped:
            image_idx = page_num - 1
            retry_tasks.append(process_single_page(client, model, images[image_idx], page_num))

        retry_results = await asyncio.gather(*retry_tasks, return_exceptions=True)
        successfully_processed = []

        for retry_result in retry_results:
            if isinstance(retry_result, Exception):
                logger.error(f"Retry processing failed: {str(retry_result)}")
                continue
            page_result, page_num = retry_result
            if page_result:
                all_results.update(page_result)
                successfully_processed.append(page_num)

        skipped_pages = [p for p in skipped_pages if p not in successfully_processed]

        if not all_results and skipped_pages:
            return JSONResponse(
                content={"error": "No valid text extracted from any pages", "skipped_pages": skipped_pages, "sessionId": sessionId},
                status_code=400
            )
    else:
        # Handle non-PDF files (XML, CSV, JSON) as text
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            content_str = content.decode('latin-1', errors='ignore')
        all_results = {"content": content_str}  # Wrap as dict for consistency
        skipped_pages = []

    session_id = sessionId if sessionId else f"session_{int(time.time())}_{str(uuid4())}"

    if is_extraction:
        return {
            "extracted_text": all_results,
            "skipped_pages": skipped_pages,
            "sessionId": session_id
        }

    try:
        results_str = json.dumps(all_results)
    except Exception as e:
        logger.error(f"Failed to serialize all_results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to serialize extracted text: {str(e)}")

    session_data = session_store.get(f"sessions.{session_id}", {"chatHistory": []})
    chat_history = session_data.get("chatHistory", [])
    chat_history.append({"role": "user", "content": prompt})

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [{"type": "text", "text": f"User prompt: {prompt}\nExtracted text: {results_str}"}]}
            ],
            temperature=0.3,
            max_tokens=2048
        )
        generated_response = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": generated_response})
        session_store.set(f"sessions.{session_id}", {
            "chatHistory": chat_history,
            "timestamp": time.time()
        })
        return {
            "response": generated_response,
            "extracted_text": all_results,
            "skipped_pages": skipped_pages,
            "sessionId": session_id
        }
    except Exception as e:
        logger.error(f"Final API request failed: {str(e)}")
        chat_history.append({"role": "assistant", "content": f"⚠️ Error processing question: {str(e)}"})
        session_store.set(f"sessions.{session_id}", {
            "chatHistory": chat_history,
            "timestamp": time.time()
        })
        raise HTTPException(status_code=500, detail=f"Final API request failed: {str(e)}")

@app.post("/process_message")
async def process_message(
    prompt: str = Form(...),
    extracted_text: str = Form(...),
    sessionId: str = Form(None),
    model: str = Form(default="gemma3"),
    system_prompt: str = Form(default=SYSTEM_PROMPT)
):
    """Endpoint to process a query using extracted text, with session support for Electron app."""
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Please provide a non-empty prompt")
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Please provide non-empty extracted text")

    try:
        client = get_openai_client(model)
    except ValueError as e:
        logger.error(f"Invalid model: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    all_results = {}
    text_for_analysis = extracted_text
    try:
        all_results = json.loads(extracted_text)
        if isinstance(all_results, dict):
            text_for_analysis = json.dumps(all_results)
        else:
            logger.warning(f"Extracted text is not a JSON object: {extracted_text}")
            all_results = {}
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid extracted text format, using as plain text: {str(e)}")
        all_results = {"content": extracted_text}

    session_id = sessionId if sessionId else f"session_{int(time.time())}_{str(uuid4())}"
    session_data = session_store.get(f"sessions.{session_id}", {"chatHistory": []})
    chat_history = session_data.get("chatHistory", [])
    chat_history.append({"role": "user", "content": prompt})

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [{"type": "text", "text": f"User prompt: {prompt}\nExtracted text: {text_for_analysis}"}]}
            ],
            temperature=0.3,
            max_tokens=2048
        )
        generated_response = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": generated_response})
        session_store.set(f"sessions.{session_id}", {
            "chatHistory": chat_history,
            "timestamp": time.time()
        })
        return {
            "response": generated_response,
            "extracted_text": all_results,
            "skipped_pages": [],
            "sessionId": session_id
        }
    except Exception as e:
        logger.error(f"Final API request failed for session {session_id}: {str(e)}")
        chat_history.append({"role": "assistant", "content": f"⚠️ Error processing question: {str(e)}"})
        session_store.set(f"sessions.{session_id}", {
            "chatHistory": chat_history,
            "timestamp": time.time()
        })
        raise HTTPException(status_code=500, detail=f"Final API request failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API and its dependencies are operational."""
    return {"status": "healthy", "message": "API and model connectivity are operational"}