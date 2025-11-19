from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, dependencies

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/{entity_type}/{entity_id}", response_model=list[schemas.ConnectionResponse])
def get_entity_graph(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(dependencies.get_db)
):
    if entity_type not in ["legal", "natural"]:
        raise HTTPException(400, "entity_type must be 'legal' or 'natural'")
    connections = crud.get_connections_for_entity(db, entity_type, entity_id)
    return connections

@router.post("/connections", response_model=schemas.ConnectionResponse, status_code=201)
def add_connection(conn: schemas.ConnectionCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_connection(db, conn)