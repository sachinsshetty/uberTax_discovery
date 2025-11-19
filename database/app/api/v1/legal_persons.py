from fastapi import APIRouter, Depends, HTTPException
from app.schemas.legal_person import LegalPersonCreate, LegalPersonOut
from app.crud import legal_person as crud
from app.core.database import AsyncSession, get_db

router = APIRouter()

@router.post("/", response_model=LegalPersonOut, status_code=201)
async def create_legal_person(payload: LegalPersonCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create(db=db, obj_in=payload)