import gradio as gr
import requests
import logging
import os
import json
import concurrent.futures
from typing import List, Dict, Tuple, Optional
from time import time
import argparse
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration
DWANI_API_BASE_URL = os.getenv('DWANI_API_BASE_URL', '0.0.0.0')
API_URL_PDF = f"http://{DWANI_API_BASE_URL}:18889/process_pdf"
API_URL_MESSAGE = f"http://{DWANI_API_BASE_URL}:18889/process_message"
API_URL_HEALTH = f"http://{DWANI_API_BASE_URL}:18889/health"
MAX_FILE_SIZE_MB = 10  # Max PDF size in MB
MAX_CONCURRENT_PDFS = 5  # Max PDFs to process concurrently

def validate_config() -> None:
    """Validate environment configuration at startup."""
    if DWANI_API_BASE_URL == '0.0.0.0':
        logger.warning("DWANI_API_BASE_URL not set, using default '0.0.0.0'. This may cause issues in production.")
    try:
        response = requests.get(API_URL_HEALTH, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to connect to API server at {DWANI_API_BASE_URL}: {str(e)}")
        raise

def validate_pdf(file_path: str) -> bool:
    """Validate PDF file for type and size."""
    if not file_path.lower().endswith('.pdf'):
        logger.warning(f"Invalid file type: {file_path}")
        return False
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            logger.warning(f"File {file_path} exceeds size limit of {MAX_FILE_SIZE_MB}MB")
            return False
        return True
    except OSError as e:
        logger.error(f"Error accessing file {file_path}: {str(e)}")
        return False

def extract_single_pdf(pdf_path: str, session_id: str) -> Dict:
    """Extract text from a single PDF using the server endpoint."""
    if not validate_pdf(pdf_path):
        return {'extracted_text': {}, 'skipped_pages': [], 'sessionId': session_id}
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
            data = {
                "prompt": "Extract all text from this PDF.",
                "sessionId": session_id,
                "is_extraction": True
            }
            response = requests.post(API_URL_PDF, files=files, data=data, timeout=90)
            response.raise_for_status()
            result = response.json()
            return {
                'extracted_text': result.get('extracted_text', {}),
                'skipped_pages': result.get('skipped_pages', []),
                'sessionId': result.get('sessionId', session_id)
            }
    except requests.RequestException as e:
        logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
        return {'extracted_text': {}, 'skipped_pages': [], 'sessionId': session_id}
    except Exception as e:
        logger.error(f"Unexpected error extracting text from {pdf_path}: {str(e)}")
        return {'extracted_text': {}, 'skipped_pages': [], 'sessionId': session_id}

def extract_texts(pdf_paths: List[str], session_id: str) -> Tuple[str, str]:
    """Extract text from multiple PDFs in parallel and return combined JSON-serialized text and session ID."""
    valid_paths = [p for p in pdf_paths if validate_pdf(p)]
    if not valid_paths:
        return "{}", session_id

    # Extract texts in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(valid_paths), MAX_CONCURRENT_PDFS)) as executor:
        results = list(executor.map(lambda p: extract_single_pdf(p, session_id), valid_paths))

    # Combine texts into a nested dict {filename: {page: text, ...}} and update session ID
    combined_extracted = {}
    final_session_id = session_id
    for path, result in zip(valid_paths, results):
        extracted_dict = result['extracted_text']
        if isinstance(extracted_dict, dict) and extracted_dict:
            basename = os.path.splitext(os.path.basename(path))[0]  # Remove .pdf extension
            combined_extracted[basename] = extracted_dict
        if result['skipped_pages']:
            logger.warning(f"Skipped pages in {path}: {result['skipped_pages']}")
        final_session_id = result['sessionId']  # Update with the latest session ID from server

    return json.dumps(combined_extracted), final_session_id

def process_message(history: List[Dict], message: str, pdf_files: Optional[List[str]], session_id: str, language: str, extracted_text_state: str) -> Tuple[List[Dict], str, str, str, str]:
    """Handle chat messages, using server session management. Extracts text only on first query if not already stored."""
    pdf_files = pdf_files or []
    current_paths = sorted([f for f in pdf_files if f])  # List of file paths

    # Validate input
    if not message.strip():
        return history + [{"role": "user", "content": message}, {"role": "assistant", "content": "⚠️ Please enter a valid question!"}], "", session_id, language, extracted_text_state

    if not current_paths and not extracted_text_state:
        return history + [{"role": "user", "content": message}, {"role": "assistant", "content": "⚠️ Please upload at least one PDF first!"}], "", session_id, language, extracted_text_state

    # Extract if not already done
    if not extracted_text_state and current_paths:
        extracted_json, new_session_id = extract_texts(current_paths, session_id)
        if not extracted_json or extracted_json == "{}":
            return history + [{"role": "user", "content": message}, {"role": "assistant", "content": "⚠️ No text could be extracted from the provided PDFs!"}], "", new_session_id, language, ""
        text_for_api = extracted_json
        update_extracted_state = extracted_json
    elif extracted_text_state:
        text_for_api = extracted_text_state
        new_session_id = session_id
        update_extracted_state = extracted_text_state
    else:
        return history + [{"role": "user", "content": message}, {"role": "assistant", "content": "⚠️ No extracted text available!"}], "", session_id, language, extracted_text_state

    try:
        # Send query to API
        data = {
            "prompt": f"Answer in {language}: {message}",
            "extracted_text": text_for_api,
            "sessionId": new_session_id
        }
        response = requests.post(API_URL_MESSAGE, data=data, timeout=90)
        response.raise_for_status()
        result = response.json()

        # Update history with server response
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": result['response']})
        return history, "", result['sessionId'], language, update_extracted_state
    except requests.RequestException as e:
        logger.error(f"API request failed for session {session_id}: {str(e)}")
        return history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: Failed to process your request. Please try again later."}], "", new_session_id, language, update_extracted_state
    except Exception as e:
        logger.error(f"Unexpected error for session {session_id}: {str(e)}")
        return history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {str(e)}"}], "", new_session_id, language, update_extracted_state

def clear_chat(session_id: str) -> List:
    """Clear the chat history for a session."""
    return []

def new_chat(session_id: str, language: str) -> Tuple[List, None, str, str, str]:
    """Clear chat history and reset PDF state for a session."""
    return [], None, f"session_{int(time())}", "English", ""

# Custom styling
css = """
.gradio-container { max-width: 1200px; margin: auto; }
#chatbot { height: calc(100vh - 200px); max-height: 800px; }
#message { resize: none; }
"""

def create_gradio_app() -> gr.Blocks:
    """Create and configure the Gradio application."""
    instructions_text = f"""
    1. Upload one or more PDF documents (max {MAX_FILE_SIZE_MB}MB each).  
    2. Ask questions about the documents in the chat box.  
    3. The assistant will respond based on the documents' content.  
    4. Use 'Clear Chat' to reset the conversation history.  
    5. Use 'New Chat' to start a new session (clears chat and PDFs).  
    """

    with gr.Blocks(title="dwani.ai - Discovery", css=css, fill_width=True) as demo:
        gr.Markdown("# 📄 UberTax - Agentic Tax Analytics")

        # Generate a unique session ID
        session_id = gr.State(value=f"session_{int(time())}")
        extracted_text = gr.State(value="")

        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                [],
                elem_id="chatbot",
                label="Document Assistant",
                type="messages"
            )
            msg = gr.Textbox(
                placeholder="Ask something about the document...",
                label="Your Question",
                elem_id="message"
            )
            pdf_input = gr.File(
                label=f"Attach PDFs (max {MAX_FILE_SIZE_MB}MB each, upload once per session)",
                file_types=[".pdf"],
                file_count="multiple"
            )
            language = gr.Dropdown(
                choices=["English", "Spanish", "French", "German"],
                value="English",
                label="Response Language"
            )
            with gr.Row():
                clear = gr.Button("Clear Chat")
                new_chat_button = gr.Button("New Chat")

            with gr.Accordion("Instructions", open=False):
                gr.Markdown(instructions_text)

        # Event bindings
        msg.submit(
            process_message,
            inputs=[chatbot, msg, pdf_input, session_id, language, extracted_text],
            outputs=[chatbot, msg, session_id, language, extracted_text]
        )
        clear.click(
            clear_chat,
            inputs=[session_id],
            outputs=[chatbot]
        )
        new_chat_button.click(
            new_chat,
            inputs=[session_id, language],
            outputs=[chatbot, pdf_input, session_id, language, extracted_text]
        )

    return demo

def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description="UberTax - Agentic Tax Analytics")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    args = parser.parse_args()

    try:
        validate_config()
        demo = create_gradio_app()
        demo.launch(server_name=args.host, server_port=args.port, show_error=True)
    except Exception as e:
        logger.error(f"Failed to launch Gradio interface: {str(e)}")
        print(f"Failed to launch Gradio interface: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()