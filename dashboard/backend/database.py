# File: database.py (updated)
import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import csv
from datetime import date
from constants import MOCK_DATA_CSV, REGULATORY_FEED_CSV  # Assuming REGULATORY_FEED_CSV is added to constants.py
from enum import Enum

logger = logging.getLogger(__name__)

# Define Status Enum for consistency
class StatusEnum(str, Enum):
    PENDING = "pending"
    LIVE = "LIVE"
    # Add other statuses as needed, e.g., COMPLETED = "completed", EXPIRED = "expired"

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "app.db")
db_dir = Path(SQLITE_DB_PATH).parent
db_dir.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, index=True)  # Added unique=True for integrity
    company_name = Column(String)
    country = Column(String)
    new_regulation = Column(String)
    deadline = Column(Date)
    status = Column(SQLEnum(StatusEnum, name="client_status"), default=StatusEnum.PENDING)  # Use Enum with default

class RegulatoryFeed(Base):
    __tablename__ = "regulatory_feed"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    country = Column(String, nullable=False)
    content = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def startup_event():
    db = SessionLocal()
    try:
        # Handle ClientProfile mock data insertion
        if db.query(ClientProfile).count() == 0:
            if not MOCK_DATA_CSV.exists():
                logger.warning(f"Mock data CSV file not found at {MOCK_DATA_CSV}. Skipping mock data insertion.")
            else:
                try:
                    mock_data = []
                    with open(MOCK_DATA_CSV, 'r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            data = {
                                "client_id": row.get('client_id'),
                                "company_name": row.get('company_name'),
                                "country": row.get('country'),
                                "new_regulation": row.get('new_regulation'),
                                "deadline": row.get('deadline'),
                                "status": row.get('status'),
                            }
                            mock_data.append(data)
                    
                    logger.info(f"Loaded {len(mock_data)} client profiles from CSV.")
                except Exception as e:
                    logger.error(f"Failed to load mock data CSV: {str(e)}. Skipping mock data insertion.")
                    mock_data = []

                for data in mock_data:
                    # Check for duplicates before adding
                    if db.query(ClientProfile).filter(ClientProfile.client_id == data["client_id"]).first():
                        logger.info(f"Skipping existing client {data['client_id']}.")
                        continue
                    
                    parsed_data = data.copy()
                    if data["deadline"] and isinstance(data["deadline"], str) and data["deadline"].strip():
                        try:
                            parsed_data["deadline"] = date.fromisoformat(data["deadline"].strip())
                        except ValueError:
                            logger.warning(f"Invalid deadline format '{data['deadline']}' for client {data['client_id']}. Setting to None.")
                            parsed_data["deadline"] = None
                    else:
                        parsed_data["deadline"] = None
                    
                    # Map string status to Enum
                    try:
                        parsed_data["status"] = StatusEnum(parsed_data["status"])
                    except ValueError:
                        logger.warning(f"Invalid status '{parsed_data['status']}' for client {data['client_id']}. Setting to PENDING.")
                        parsed_data["status"] = StatusEnum.PENDING
                    
                    client = ClientProfile(**parsed_data)
                    db.add(client)
                db.commit()
                logger.info("Mock data inserted successfully.")

        # Handle RegulatoryFeed mock data insertion
        if db.query(RegulatoryFeed).count() == 0:
            if not REGULATORY_FEED_CSV.exists():
                logger.warning(f"Regulatory feed CSV file not found at {REGULATORY_FEED_CSV}. Skipping regulatory feed data insertion.")
            else:
                try:
                    feed_data = []
                    with open(REGULATORY_FEED_CSV, 'r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            data = {
                                "date": row.get('date'),
                                "country": row.get('country'),
                                "content": row.get('content'),
                            }
                            feed_data.append(data)
                    
                    logger.info(f"Loaded {len(feed_data)} regulatory feed items from CSV.")
                except Exception as e:
                    logger.error(f"Failed to load regulatory feed CSV: {str(e)}. Skipping regulatory feed data insertion.")
                    feed_data = []

                for data in feed_data:
                    # Optional: Check for duplicates, e.g., by unique combination of date and country if needed
                    # For now, insert all as they might not have unique constraints beyond id
                    feed_item = RegulatoryFeed(**data)
                    db.add(feed_item)
                db.commit()
                logger.info(f"Inserted {len(feed_data)} regulatory feed items.")
    finally:
        db.close()