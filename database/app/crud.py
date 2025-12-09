# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from . import models, schemas


# ==================== LEGAL & NATURAL PERSONS (100% your original) ====================
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
    if not db_lp: return None
    for k, v in lp.model_dump(exclude_unset=True).items():
        setattr(db_lp, k, v)
    db.commit()
    db.refresh(db_lp)
    return db_lp


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
    if not db_np: return None
    for k, v in np.model_dump(exclude_unset=True).items():
        setattr(db_np, k, v)
    db.commit()
    db.refresh(db_np)
    return db_np


# ==================== GRAPH CONNECTIONS + TRAVERSAL ====================

def create_connection(db: Session, conn: schemas.ConnectionCreate):
    sql = text("""
        INSERT INTO entity_connections 
        (from_type, from_id, to_type, to_id, relation, share_percentage)
        VALUES (:from_type, :from_id, :to_type, :to_id, :relation, :share_percentage)
        RETURNING *
    """)
    result = db.execute(sql, conn.model_dump())
    db.commit()
    return result.fetchone()


def get_connections_for_entity(db: Session, entity_type: str, entity_id: int):
    sql = text("""
        SELECT * FROM entity_connections 
        WHERE from_type = :etype AND from_id = :eid
        ORDER BY share_percentage DESC NULLS LAST
    """)
    return db.execute(sql, {"etype": entity_type, "eid": entity_id}).fetchall()


def get_connection_by_id(db: Session, conn_id: int):
    sql = text("SELECT * FROM entity_connections WHERE id = :id")
    return db.execute(sql, {"id": conn_id}).fetchone()


def update_connection(db: Session, conn_id: int, update_data: schemas.ConnectionCreate):
    data = update_data.model_dump(exclude_unset=True)
    if not data: return None
    set_clause = ", ".join(f"{k} = :{k}" for k in data)
    sql = text(f"UPDATE entity_connections SET {set_clause}, updated_at = now() WHERE id = :id RETURNING *")
    data["id"] = conn_id
    result = db.execute(sql, data)
    db.commit()
    return result.fetchone()


def delete_connection(db: Session, conn_id: int):
    sql = text("DELETE FROM entity_connections WHERE id = :id RETURNING id")
    result = db.execute(sql, {"id": conn_id})
    deleted = result.fetchone()
    if deleted:
        db.commit()
        return True
    return False


# ====================== GRAPH TRAVERSAL ======================

def get_downstream_ownership(db: Session, entity_type: str, entity_id: int, max_depth: int = 10):
    sql = text("""
        WITH RECURSIVE path AS (
            SELECT from_type, from_id, to_type, to_id, relation, share_percentage, 1 as depth,
                   ARRAY[from_id, to_id] as path
            FROM entity_connections
            WHERE from_type = :etype AND from_id = :eid

            UNION ALL

            SELECT e.from_type, e.from_id, e.to_type, e.to_id, e.relation, e.share_percentage,
                   p.depth + 1, p.path || e.to_id
            FROM entity_connections e
            JOIN path p ON e.from_type = p.to_type AND e.from_id = p.to_id
            WHERE p.depth < :max_depth AND NOT (e.to_id = ANY(p.path))
        )
        SELECT * FROM path ORDER BY depth, share_percentage DESC NULLS LAST
    """)
    result = db.execute(sql, {"etype": entity_type, "eid": entity_id, "max_depth": max_depth})
    return [dict(r._mapping) for r in result.fetchall()]


def get_ultimate_beneficial_owners(db: Session, entity_type: str, entity_id: int,
                                   min_shareholding: float = 25.0, max_depth: int = 10):
    sql = text("""
        WITH RECURSIVE ownership AS (
            SELECT e.from_id as person_id, e.share_percentage as effective,
                   1 as depth, ARRAY[e.from_id] as path
            FROM entity_connections e
            WHERE e.to_type = :etype AND e.to_id = :eid AND e.from_type = 'natural'

            UNION ALL

            SELECT e.from_id, o.effective * (e.share_percentage / 100.0),
                   o.depth + 1, o.path || e.from_id
            FROM entity_connections e
            JOIN ownership o ON e.to_type = 'legal' AND e.to_id = o.person_id
            WHERE o.depth < :max_depth AND NOT (e.from_id = ANY(o.path))
        )
        SELECT person_id, ROUND(effective::numeric, 4) as effective_shareholding, depth
        FROM ownership
        WHERE effective >= :min_share
        ORDER BY effective DESC
    """)
    result = db.execute(sql, {
        "etype": entity_type, "eid": entity_id,
        "min_share": min_shareholding, "max_depth": max_depth
    })
    return [dict(r._mapping) for r in result.fetchall()]


def get_control_path_from_person(db: Session, person_id: int, entity_type: str, entity_id: int):
    sql = text("""
        WITH RECURSIVE path AS (
            SELECT from_type, from_id, to_type, to_id, relation, share_percentage, 1 as depth
            FROM entity_connections
            WHERE from_type = 'natural' AND from_id = :person_id

            UNION ALL

            SELECT e.from_type, e.from_id, e.to_type, e.to_id, e.relation, e.share_percentage, p.depth + 1
            FROM entity_connections e
            JOIN path p ON e.from_type = p.to_type AND e.from_id = p.to_id
            WHERE p.depth < 20
        )
        SELECT depth, relation, share_percentage, to_type, to_id
        FROM path
        WHERE to_type = :etype AND to_id = :eid
        ORDER BY depth
    """)
    result = db.execute(sql, {"person_id": person_id, "etype": entity_type, "eid": entity_id})
    return [dict(r._mapping) for r in result.fetchall()]