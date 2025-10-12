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
    allow_origins=["*"],  # Temp for dev; restrict to ["http://localhost:3000"] in prod
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
            # New entries based on e-invoicing analysis
            {
                "client_id": "CI2001",
                "company_name": "Split Hospitality Group j.d.o.o.",
                "country": "Croatia",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            },
            {
                "client_id": "CI2002",
                "company_name": "KreativWerkstatt S.C.",
                "country": "Poland",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            },
            {
                "client_id": "CI2003",
                "company_name": "Global Dynamics Sp. z o.o.",
                "country": "Poland",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            },
            {
                "client_id": "CI2004",
                "company_name": "Copenhagen Consulting ApS",
                "country": "Denmark",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            },
            {
                "client_id": "CI2005",
                "company_name": "Adriatic Solutions d.o.o.",
                "country": "Croatia",
                "new_regulation": "Croatian B2B e-Invoicing Mandate",
                "deadline": "2026-01-01",
                "status": "MONITORED"
            },
            {
                "client_id": "CI2006",
                "company_name": "Aarhus Retail IVS",
                "country": "Denmark",
                "new_regulation": "N/A",
                "deadline": None,
                "status": "LIVE"
            }
        ]
        for data in mock_data:
            # Parse deadline string to date object if present
            parsed_data = data.copy()
            if data["deadline"] is not None and isinstance(data["deadline"], str):
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
             "newRegulation": c.new_regulation, "deadline": c.deadline.isoformat() if c.deadline else None,
             "status": c.status} for c in clients]