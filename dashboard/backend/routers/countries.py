# File: routers/clients.py (minor tweaks for robustness)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, ClientProfile
from schemas import RegulatoryFeed  # Updated schemas
from datetime import date
from typing import List
from pydantic import Field, BaseModel  # If using explicit Fields in schemas

import os
from openai import OpenAI
import json
from sqlalchemy import text
from typing import Any, Dict


router = APIRouter(prefix="/api/countries", tags=["countries"])

@router.get("/regulatory-feed", response_model=List[RegulatoryFeed])
async def get_regulatory_feed():
    """
    Fetch regulatory feed items with Pydantic validation.
    For now, returns hardcoded data; in production, fetch from DB or external source.
    """
    feed_data = [
        {
            "date": "Oct 9, 2025",
            "country": "USA",
            "content": "IRS releases tax inflation adjustments for tax year 2026, including amendments from the One Big Beautiful Bill; standard deduction raised to $15,750 for singles and $31,500 for married filing jointly."
        },
        {
            "date": "Oct 9, 2025",
            "country": "USA",
            "content": "IRS 2025-2026 Priority Guidance Plan outlines key focus areas amid government shutdown impacts."
        },
        {
            "date": "Oct 10, 2025",
            "country": "USA",
            "content": "Treasury and IRS issue proposed regulations for “No Tax on Tips” provision under OBBBA, allowing deduction up to $25,000 for qualified tips."
        },
        {
            "date": "Oct 4, 2025",
            "country": "USA",
            "content": "One Big Beautiful Bill Act (passed July 2025) introduces $6,000 deduction for individuals age 65+, effective 2025-2028, plus other Trump Tax Plan changes for 2025 filings."
        }
    ]
    return feed_data