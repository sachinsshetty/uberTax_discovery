from sqlalchemy.orm import Session
from . import models, schemas

# Legal Persons
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

# Natural Persons (similar)
# ... (omitted for brevity – same pattern)

# Graph connections
def create_connection(db: Session, conn: schemas.ConnectionCreate):
    db_conn = models.entity_connections.insert().values(**conn.model_dump())
    result = db.execute(db_conn)
    db.commit()
    return db.execute(models.entity_connections.select().where(
        models.entity_connections.c.id == result.inserted_primary_key[0])).first()

def get_connections_for_entity(db: Session, entity_type: str, entity_id: int):
    return db.execute(
        models.entity_connections.select().where(
            (models.entity_connections.c.from_type == entity_type) &
            (models.entity_connections.c.from_id == entity_id)
        )
    ).fetchall()