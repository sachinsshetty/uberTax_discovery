from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, dependencies

router = APIRouter(prefix="/legal_persons", tags=["legal_persons"])

@router.get("/", response_model=list[schemas.LegalPerson])
def read_legal_persons(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    return crud.get_legal_persons(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=schemas.LegalPerson)
def read_legal_person(id: int, db: Session = Depends(dependencies.get_db)):
    lp = crud.get_legal_person(db, id)
    if not lp:
        raise HTTPException(404, "Not found")
    return lp

@router.post("/", response_model=schemas.LegalPerson, status_code=201)
def create_legal_person(lp: schemas.LegalPersonCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_legal_person(db, lp)

@router.put("/{id}", response_model=schemas.LegalPerson)
def update_legal_person(id: int, lp: schemas.LegalPersonUpdate, db: Session = Depends(dependencies.get_db)):
    updated = crud.update_legal_person(db, id, lp)
    if not updated:
        raise HTTPException(404)
    return updated