# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models, schemas


# ==================== LEGAL PERSONS (100% unchanged) ====================
def get_legal_person(db: Session, id: int):
    return db.query(models.LegalPerson).filter(models.LegalPerson.id == id).first()

def get_legal_persons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.LegalPerson).offset(skip).limit(limit).all()

def create_legal_person(db: Session, lp: schemas.LegalPersonCreate):
    db_lp = models.LegalPerson(**lp.model_dump())
    db.add(db_lp)
    db.commit()
    db.refresh(db_lp)
    return db_lp

def update_legal_person(db: Session, id: int, lp: schemas.LegalPersonUpdate):
    db_lp = get_legal_person(db, id)
    if not db_lp:
        return None
    update_data = lp.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lp, key, value)
    db.commit()
    db.refresh(db_lp)
    return db_lp


# ==================== NATURAL PERSONS (100% unchanged) ====================
def get_natural_person(db: Session, id: int):
    return db.query(models.NaturalPerson).filter(models.NaturalPerson.id == id).first()

def get_natural_persons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.NaturalPerson).offset(skip).limit(limit).all()

def create_natural_person(db: Session, np: schemas.NaturalPersonCreate):
    db_np = models.NaturalPerson(**np.model_dump())
    db.add(db_np)
    db.commit()
    db.refresh(db_np)
    return db_np

def update_natural_person(db: Session, id: int, np: schemas.NaturalPersonUpdate):
    db_np = get_natural_person(db, id)
    if not db_np:
        return None
    update_data = np.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_np, key, value)
    db.commit()
    db.refresh(db_np)
    return db_np


# ==================== GRAPH CONNECTIONS – OPTIMIZED & FIXED ====================

def create_connection(db: Session, conn: schemas.ConnectionCreate):
    """
    Create a new connection – now in ONE query using RETURNING *
    Prevents duplicates via DB constraint (added in models.py + migration)
    """
    sql = text("""
        INSERT INTO entity_connections 
        (from_type, from_id, to_type, to_id, relation, share_percentage)
        VALUES (:from_type, :from_id, :to_type, :to_id, :relation, :share_percentage)
        RETURNING *
    """)
    result = db.execute(sql, conn.model_dump())
    db.commit()
    return result.fetchone()  # Returns full row including id, created_at, etc.


def get_connections_for_entity(db: Session, entity_type: str, entity_id: int):
    """
    Get all outgoing connections from an entity
    Now lightning-fast thanks to composite index: (from_type, from_id)
    """
    sql = text("""
        SELECT * FROM entity_connections 
        WHERE from_type = :etype 
          AND from_id = :eid
        ORDER BY share_percentage DESC NULLS LAST, created_at DESC
    """)
    return db.execute(sql, {"etype": entity_type, "eid": entity_id}).fetchall()


def get_connection_by_id(db: Session, conn_id: int):
    """Helper: get single connection by primary key (O(1) instant)"""
    sql = text("SELECT * FROM entity_connections WHERE id = :id")
    return db.execute(sql, {"id": conn_id}).fetchone()


def update_connection(db: Session, conn_id: int, update_data: schemas.ConnectionCreate):
    """
    Partial update of a connection
    Only provided fields are updated
    """
    data = update_data.model_dump(exclude_unset=True)
    if not data:
        return None

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
    return result.fetchone()


def delete_connection(db: Session, conn_id: int):
    """
    Hard delete (you can later change to soft delete if needed)
    Returns True if deleted
    """
    sql = text("""
        DELETE FROM entity_connections 
        WHERE id = :id 
        RETURNING id
    """)
    result = db.execute(sql, {"id": conn_id})
    deleted = result.fetchone()
    if deleted:
        db.commit()
        return True
    return False