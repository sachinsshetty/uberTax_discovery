# app/routers/graph.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter(prefix="/graph", tags=["Ownership Graph"])


@router.get(
    "/{entity_type}/{entity_id}",
    response_model=List[schemas.ConnectionResponse]
)
def get_connections(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db)
):
    if entity_type not in {"legal", "natural"}:
        raise HTTPException(
            status_code=400,
            detail="entity_type must be 'legal' or 'natural'"
        )
    connections = crud.get_connections_for_entity(db, entity_type, entity_id)
    return connections


@router.post(
    "/connections",
    response_model=schemas.ConnectionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_connection(
    conn: schemas.ConnectionCreate,
    db: Session = Depends(get_db)
):
    return crud.create_connection(db, conn)