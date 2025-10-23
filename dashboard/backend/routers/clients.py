# File: routers/clients.py (minor tweaks for robustness)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, ClientProfile
from schemas import ClientProfileCreate, ClientProfileUpdate, ClientProfileResponse  # Updated schemas
from datetime import date
from typing import List
from pydantic import Field  # If using explicit Fields in schemas

router = APIRouter(prefix="/api/clients", tags=["clients"])

@router.get("/", response_model=List[ClientProfileResponse])
async def get_clients(db: Session = Depends(get_db)):
    """Fetch all client profiles with Pydantic validation."""
    clients = db.query(ClientProfile).all()
    return clients  # Now serializes correctly with aliases

@router.post("/", response_model=ClientProfileResponse, status_code=201)
async def create_client(
    client: ClientProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new client profile with Pydantic validation."""
    # Check if client_id already exists
    existing = db.query(ClientProfile).filter(ClientProfile.client_id == client.client_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Client ID already exists")
    
    # Parse deadline
    deadline_date = None
    if client.deadline:
        try:
            deadline_date = date.fromisoformat(client.deadline)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline format. Use ISO format (YYYY-MM-DD).")
    
    db_client = ClientProfile(
        client_id=client.client_id,
        company_name=client.company_name,
        country=client.country,
        new_regulation=client.new_regulation,
        deadline=deadline_date,
        status=client.status
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client  # Serializes to camelCase JSON

@router.put("/{client_id}", response_model=ClientProfileResponse)
async def update_client(
    client_id: str,
    update_data: ClientProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing client profile with Pydantic validation."""
    db_client = db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    if "deadline" in update_dict and update_dict["deadline"]:
        try:
            update_dict["deadline"] = date.fromisoformat(update_dict["deadline"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline format. Use ISO format (YYYY-MM-DD).")
    else:
        update_dict["deadline"] = None
    
    for field, value in update_dict.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: str,
    db: Session = Depends(get_db)
):
    """Delete a client profile."""
    db_client = db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return None