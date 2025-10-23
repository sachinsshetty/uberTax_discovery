# File: database.py
import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import csv
from datetime import date
from constants import MOCK_DATA_CSV

logger = logging.getLogger(__name__)

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "app.db")
db_dir = Path(SQLITE_DB_PATH).parent
db_dir.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True)
    company_name = Column(String)
    country = Column(String)
    new_regulation = Column(String)
    deadline = Column(Date)
    status = Column(String)

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
        if db.query(ClientProfile).count() == 0:
            if not MOCK_DATA_CSV.exists():
                logger.warning(f"Mock data CSV file not found at {MOCK_DATA_CSV}. Skipping mock data insertion.")
                return
            
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
                return

            for data in mock_data:
                parsed_data = data.copy()
                if data["deadline"] and isinstance(data["deadline"], str) and data["deadline"].strip():
                    try:
                        parsed_data["deadline"] = date.fromisoformat(data["deadline"].strip())
                    except ValueError:
                        logger.warning(f"Invalid deadline format '{data['deadline']}' for client {data['client_id']}. Setting to None.")
                        parsed_data["deadline"] = None
                else:
                    parsed_data["deadline"] = None
                client = ClientProfile(**parsed_data)
                db.add(client)
            db.commit()
            logger.info("Mock data inserted successfully.")
    finally:
        db.close()