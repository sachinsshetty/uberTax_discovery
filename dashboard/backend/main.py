# File: main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware import TimingMiddleware
from routers import clients, process
from database import startup_event

from logging_config import logger  # Import logger from the config module

app = FastAPI(title="Juris-Diction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TimingMiddleware)

app.include_router(clients.router)
app.include_router(process.router)

@app.on_event("startup")
async def startup():
    await startup_event()

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API and its dependencies are operational."""
    return {"status": "healthy", "message": "API and model connectivity are operational"}