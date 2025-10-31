# File: constants.py
import os
from pathlib import Path
SYSTEM_PROMPT = """1. CORE IDENTITY & PERSONA\n\nYou are \"Juris-Diction(AI)ry\", a highly specialized AI assistant designed for tax professionals. [...]"""  # Full prompt here (truncated for brevity)
MASTER_PROMPT = ""  # Fixed spacing; populate if needed
SESSION_FILE = Path("/app/data/sessions.json")  # Absolute path for Docker persistence
MOCK_DATA_JSON = Path("mock_data.json")  # Path to CSV file containing mock data
REGULATORY_FEED_JSON = Path("mock_regulatory_feed.json")
DWANI_API_BASE_URL = os.getenv('DWANI_API_BASE_URL')