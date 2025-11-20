# app/routers/natural_persons.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter(prefix="/natural-persons", tags=["Natural Persons"])


@router.get("/", response_model=List[schemas.NaturalPerson])
def list_natural_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_natural_persons(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=schemas.NaturalPerson)
def get_natural_person(
    id: int,
    db: Session = Depends(get_db)
):
    person = crud.get_natural_person(db, id)
    if not person:
        raise HTTPException(status_code=404, detail="Natural person not found")
    return person


@router.post(
    "/",
    response_model=schemas.NaturalPerson,
    status_code=status.HTTP_201_CREATED
)
def create_natural_person(
    person: schemas.NaturalPersonCreate,
    db: Session = Depends(get_db)
):
    return crud.create_natural_person(db, person)


@router.put("/{id}", response_model=schemas.NaturalPerson)
def update_natural_person(
    id: int,
    person: schemas.NaturalPersonUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_natural_person(db, id, person)
    if not updated:
        raise HTTPException(status_code=404, detail="Natural person not found")
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_natural_person(
    id: int,
    db: Session = Depends(get_db)
):
    person = crud.get_natural_person(db, id)
    if not person:
        raise HTTPException(status_code=404, detail="Natural person not found")
    db.delete(person)
    db.commit()
    return None