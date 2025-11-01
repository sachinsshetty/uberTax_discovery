# File: routers/countries.py (updated - use CountryProfile for response)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, RegulatoryFeed, CountryProfile as DBCountryProfile
from schemas import RegulatoryFeedResponse, CountryProfile
from typing import List

router = APIRouter(prefix="/api/countries", tags=["countries"])

@router.get("/regulatory-feed", response_model=List[RegulatoryFeedResponse])
async def get_regulatory_feed(db: Session = Depends(get_db)):
    """
    Fetch regulatory feed items from the database with Pydantic validation.
    """
    feed_items = db.query(RegulatoryFeed).all()
    return feed_items

@router.get("/profiles", response_model=List[CountryProfile])
async def get_country_profiles(db: Session = Depends(get_db)):
    """
    Fetch all country profiles from the database.
    """
    profiles = db.query(DBCountryProfile).all()
    return [CountryProfile.from_orm(profile) for profile in profiles]