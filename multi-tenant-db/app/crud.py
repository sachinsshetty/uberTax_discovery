from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models, schemas

# ==================== LEGAL PERSONS ====================
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


# ==================== NATURAL PERSONS ====================
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


# ==================== GRAPH CONNECTIONS ====================
def create_connection(db: Session, conn: schemas.ConnectionCreate):
    sql = text("""
        INSERT INTO entity_connections 
        (from_type, from_id, to_type, to_id, relation, share_percentage)
        VALUES (:from_type, :from_id, :to_type, :to_id, :relation, :share_percentage)
        RETURNING id
    """)
    result = db.execute(sql, conn.model_dump())
    conn_id = result.scalar()
    db.commit()
    # Return full row
    row = db.execute(
        text("SELECT * FROM entity_connections WHERE id = :id"), {"id": conn_id}
    ).fetchone()
    return row

def get_connections_for_entity(db: Session, entity_type: str, entity_id: int):
    sql = text("""
        SELECT * FROM entity_connections 
        WHERE from_type = :etype AND from_id = :eid
    """)
    return db.execute(sql, {"etype": entity_type, "eid": entity_id}).fetchall()