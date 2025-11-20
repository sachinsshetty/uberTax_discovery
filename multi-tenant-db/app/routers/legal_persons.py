# app/routers/legal_persons.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter(prefix="/legal-persons", tags=["Legal Persons"])


@router.get("/", response_model=List[schemas.LegalPerson])
def list_legal_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_legal_persons(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=schemas.LegalPerson)
def get_legal_person(
    id: int,
    db: Session = Depends(get_db)
):
    lp = crud.get_legal_person(db, id)
    if not lp:
        raise HTTPException(status_code=404, detail="Legal person not found")
    return lp


@router.post(
    "/",
    response_model=schemas.LegalPerson,
    status_code=status.HTTP_201_CREATED
)
def create_legal_person(
    lp: schemas.LegalPersonCreate,
    db: Session = Depends(get_db)
):
    return crud.create_legal_person(db, lp)


@router.put("/{id}", response_model=schemas.LegalPerson)
def update_legal_person(
    id: int,
    lp: schemas.LegalPersonUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_legal_person(db, id, lp)
    if not updated:
        raise HTTPException(status_code=404, detail="Legal person not found")
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_legal_person(
    id: int,
    db: Session = Depends(get_db)
):
    lp = crud.get_legal_person(db, id)
    if not lp:
        raise HTTPException(status_code=404, detail="Legal person not found")
    db.delete(lp)
    db.commit()
    return None