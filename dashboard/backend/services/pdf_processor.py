# File: services/pdf_processor.py
import asyncio
from typing import List, Dict
from io import BytesIO
import base64
import tempfile
import os
from fastapi import UploadFile, HTTPException
from pdf2image import convert_from_path
from services.ai_client import get_openai_client, clean_response
import json
import logging

logger = logging.getLogger(__name__)

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
        image_base64 = base64.b64encode(image_bytes_io.read()).decode("utf-8")
        
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

async def extract_text_from_pdf(content: bytes, filename: str, model: str) -> tuple[Dict, List[int]]:
    """Extract text from PDF using batches and retries."""
    all_results = {}
    skipped_pages = []

    try:
        client = get_openai_client(model)
    except ValueError as e:
        logger.error(f"Invalid model: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    if not filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for extraction")

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
                    "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes_io.read()).decode('utf-8')}"}
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
        raise HTTPException(status_code=400, detail="No valid text extracted from any pages")

    return all_results, skipped_pages