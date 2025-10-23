# File: services/ai_client.py
from openai import AsyncOpenAI
import os
import re
import json
import logging
from typing import Optional
from ..constants import DWANI_API_BASE_URL

logger = logging.getLogger(__name__)

def get_openai_client(model: str) -> AsyncOpenAI:
    """Initialize AsyncOpenAI client with model-specific base_url."""
    valid_models = ["gemma3", "gpt-oss"]
    if model not in valid_models:
        raise ValueError(f"Invalid model: {model}. Choose from: {', '.join(valid_models)}")
    
    model_ports = {
        "gemma3": "9000",
        "gpt-oss": "9500",
    }
    base_url = f"http://{DWANI_API_BASE_URL}:{model_ports[model]}/v1"
    return AsyncOpenAI(api_key="http", base_url=base_url)

def clean_response(raw_response: str) -> Optional[str]:
    """Clean markdown code blocks or other non-JSON content from the response."""
    if not raw_response:
        return None
    cleaned = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', raw_response)
    return cleaned.strip()