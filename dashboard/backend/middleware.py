# File: middleware.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from logging_config import logger  

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(f"Request: {request.method} {request.url.path} took {processing_time:.3f} seconds")
        return response