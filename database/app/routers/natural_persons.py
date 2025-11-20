from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from .. import dependencies  # now works!

router = APIRouter(prefix="/natural_persons", tags=["natural_persons"])

# Re-use the same CRUD functions (we'll add them below)
@router.get("/", response_model=List[schemas.NaturalPerson])
def read_natural_persons(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    return crud.get_natural_persons(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=schemas.NaturalPerson)
def read_natural_person(id: int, db: Session = Depends(dependencies.get_db)):
    person = crud.get_natural_person(db, id)
    if not person:
        raise HTTPException(status_code=404, detail="Natural person not found")
    return person

@router.post("/", response_model=schemas.NaturalPerson, status_code=status.HTTP_201_CREATED)
def create_natural_person(person: schemas.NaturalPersonCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_natural_person(db, person)

@router.put("/{id}", response_model=schemas.NaturalPerson)
def update_natural_person(id: int, person: schemas.NaturalPersonUpdate, db: Session = Depends(dependencies.get_db)):
    updated = crud.update_natural_person(db, id, person)
    if not updated:
        raise HTTPException(status_code=404, detail="Natural person not found")
    return updated