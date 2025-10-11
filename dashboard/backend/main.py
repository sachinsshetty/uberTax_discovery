from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date  # Added for date parsing
import os

# Database setup
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "app.db")
engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model
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

# App
app = FastAPI(title="Juris-Diction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    # Seed mock data if table is empty
    if db.query(ClientProfile).count() == 0:
        mock_data = [
            {
                "client_id": "CI0007",
                "company_name": "Innoute AG",
                "country": "Germany",
                "new_regulation": "UNDER REVIEW",
                "deadline": "2024-12-31",  # String will be parsed below
                "status": "UNDER REVIEW"
            },
            {
                "client_id": "CI0007",
                "company_name": "GlobalTech Inc.",
                "country": "USA",
                "new_regulation": "BEAT Regs (2023)",
                "deadline": "2025-03-15",
                "status": "AMENDED"
            },
            {
                "client_id": "CI6823",
                "company_name": "EuroLink SA",
                "country": "France",
                "new_regulation": "DACT Amend.",
                "deadline": "2025-01-01",
                "status": "MONITORED"
            },
            {
                "client_id": "CI8855",
                "company_name": "AsiaBridge Ltd.",
                "country": "Japan",
                "new_regulation": "MONITORED",
                "deadline": "2024-09-30",
                "status": "LIVE"
            }
        ]
        for data in mock_data:
            # Parse deadline string to date object
            parsed_data = data.copy()
            parsed_data["deadline"] = date.fromisoformat(data["deadline"])
            client = ClientProfile(**parsed_data)
            db.add(client)
        db.commit()
    db.close()

@app.get("/api/clients")
async def get_clients():
    db = SessionLocal()
    clients = db.query(ClientProfile).all()
    db.close()
    return [{"clientId": c.client_id, "companyName": c.company_name, "country": c.country,
             "newRegulation": c.new_regulation, "deadline": c.deadline.isoformat(),
             "status": c.status} for c in clients]