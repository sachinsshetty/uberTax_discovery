# File: routers/process.py
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import time
from uuid import uuid4
import json
from typing import Dict, List
from constants import SYSTEM_PROMPT
from services.ai_client import get_openai_client
from services.pdf_processor import extract_text_from_pdf
from services.session_store import session_store
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/process", tags=["process"])

@router.post("/file")
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
    content = await file.read()
    file.file.close()  # Explicit close

    all_results = {}
    skipped_pages = []

    # Handle non-PDF files as text
    file_ext = filename.split('.')[-1] if '.' in filename else ''
    if file_ext != 'pdf':
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            content_str = content.decode('latin-1', errors='ignore')
        all_results = {"content": content_str}
        skipped_pages = []
    else:
        # PDF extraction
        all_results, skipped_pages = await extract_text_from_pdf(content, filename, model)

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
        client = get_openai_client(model)
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

@router.post("/message")
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