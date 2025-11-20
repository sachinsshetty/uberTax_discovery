# routers/graph.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, dependencies

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/{entity_type}/{entity_id}", response_model=List[schemas.ConnectionResponse])
def get_outgoing_connections(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(dependencies.get_db),
):
    if entity_type not in ["legal", "natural"]:
        raise HTTPException(status_code=400, detail="entity_type must be 'legal' or 'natural'")
    
    connections = crud.get_connections_for_entity(db, entity_type, entity_id)
    return connections


@router.get("/connections/{conn_id}", response_model=schemas.ConnectionResponse)
def get_connection(conn_id: int, db: Session = Depends(dependencies.get_db)):
    conn = crud.get_connection_by_id(db, conn_id)
    if not conn or not conn.is_active:
        raise HTTPException(status_code=404, detail="Connection not found")
    return conn


@router.post("/connections", response_model=schemas.ConnectionResponse, status_code=201)
def add_connection(conn: schemas.ConnectionCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_connection(db, conn)


@router.put("/connections/{conn_id}", response_model=schemas.ConnectionResponse)
def update_connection(
    conn_id: int,
    update_data: schemas.ConnectionCreate,
    db: Session = Depends(dependencies.get_db),
):
    updated = crud.update_connection(db, conn_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Connection not found or no changes")
    return updated


@router.delete("/connections/{conn_id}", status_code=204)
def delete_connection(conn_id: int, db: Session = Depends(dependencies.get_db)):
    if not crud.delete_connection(db, conn_id):
        raise HTTPException(status_code=404, detail="Connection not found")
    return None

@router.get("/{entity_type}/{entity_id}/downstream")
def downstream(entity_type: str, entity_id: int, depth: int = 10, db: Session = Depends(get_db)):
    return crud.get_downstream_ownership(db, entity_type, entity_id, depth)

@router.get("/{entity_type}/{entity_id}/ubo")
def ubo(entity_type: str, entity_id: int, min_share: float = 25.0, db: Session = Depends(get_db)):
    return crud.get_ultimate_beneficial_owners(db, entity_type, entity_id, min_share)

@router.get("/person/{person_id}/controls/{entity_type}/{entity_id}")
def control_path(person_id: int, entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    return crud.get_control_path_from_person(db, person_id, entity_type, entity_id)