# File: routers/countries.py (updated)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, RegulatoryFeed
from schemas import RegulatoryFeedResponse
from typing import List

router = APIRouter(prefix="/api/countries", tags=["countries"])

@router.get("/regulatory-feed", response_model=List[RegulatoryFeedResponse])
async def get_regulatory_feed(db: Session = Depends(get_db)):
    """
    Fetch regulatory feed items from the database with Pydantic validation.
    """
    feed_items = db.query(RegulatoryFeed).all()
    return feed_items