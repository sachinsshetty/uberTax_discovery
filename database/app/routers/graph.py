# routers/graph.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .. import crud, schemas, dependencies

router = APIRouter(prefix="/graph", tags=["graph"])


# ==============================================================
# READ: Get outgoing connections of an entity
# ==============================================================
@router.get(
    "/{entity_type}/{entity_id}",
    response_model=List[schemas.ConnectionResponse],
    summary="Get all outgoing connections from an entity"
)
def get_outgoing_connections(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(dependencies.get_db),
):
    if entity_type not in ["legal", "natural"]:
        raise HTTPException(
            status_code=400,
            detail="entity_type must be 'legal' or 'natural'"
        )
    connections = crud.get_connections_for_entity(db, entity_type, entity_id)
    return connections


# ==============================================================
# READ: Get a single connection by ID
# ==============================================================
@router.get(
    "/connections/{conn_id}",
    response_model=schemas.ConnectionResponse,
    summary="Get a specific connection by ID"
)
def get_connection(
    conn_id: int,
    db: Session = Depends(dependencies.get_db),
):
    row = db.execute(
        text("SELECT * FROM entity_connections WHERE id = :id"),
        {"id": conn_id}
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Connection not found")
    return row


# ==============================================================
# CREATE: Add a new connection
# ==============================================================
@router.post(
    "/connections",
    response_model=schemas.ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ownership/control connection"
)
def add_connection(
    conn: schemas.ConnectionCreate,
    db: Session = Depends(dependencies.get_db),
):
    return crud.create_connection(db, conn)


# ==============================================================
# UPDATE: Update an existing connection
# ==============================================================
@router.put(
    "/connections/{conn_id}",
    response_model=schemas.ConnectionResponse,
    summary="Update a connection (e.g. change share % or relation)"
)
def update_connection(
    conn_id: int,
    update_data: schemas.ConnectionCreate,  # reuse Create schema (all fields optional in practice)
    db: Session = Depends(dependencies.get_db),
):
    # Check if exists
    exists = db.execute(
        text("SELECT 1 FROM entity_connections WHERE id = :id"),
        {"id": conn_id}
    ).fetchone()

    if not exists:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Build update dict (only non-None fields)
    data = update_data.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No data provided to update")

    # Dynamic SET clause
    set_clause = ", ".join(f"{k} = :{k}" for k in data.keys())
    sql = text(f"""
        UPDATE entity_connections
        SET {set_clause}, updated_at = now()
        WHERE id = :id
        RETURNING *
    """)

    data["id"] = conn_id
    result = db.execute(sql, data)
    db.commit()

    updated_row = result.fetchone()
    return updated_row


# ==============================================================
# DELETE: Remove a connection
# ==============================================================
@router.delete(
    "/connections/{conn_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a connection"
)
def delete_connection(
    conn_id: int,
    db: Session = Depends(dependencies.get_db),
):
    result = db.execute(
        text("DELETE FROM entity_connections WHERE id = :id RETURNING id"),
        {"id": conn_id}
    )
    deleted = result.fetchone()

    if not deleted:
        raise HTTPException(status_code=404, detail="Connection not found")

    db.commit()
    return None