# app/routers/search.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from typing import List, Dict, Any
from .. import models, schemas
from ..dependencies import get_db, get_current_tenant

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/", response_model=Dict[str, List[Any]])
def global_search(
    q: str = Query(..., min_length=2, description="Search term (min 2 chars)"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    tenant: str = Depends(get_current_tenant),  # optional: for logging/audit
):
    """
    Full-text search across Legal Persons and Natural Persons in the current tenant.
    Searches: name, registration number, tax ID, nationality, etc.
    """
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters"
        )

    search_term = f"%{q.strip().lower()}%"

    # Search Legal Persons
    legal_results = (
        db.query(models.LegalPerson)
        .filter(
            or_(
                models.LegalPerson.name.ilike(search_term),
                models.LegalPerson.registration_number.ilike(search_term),
                models.LegalPerson.jurisdiction.ilike(search_term),
            )
        )
        .limit(limit)
        .all()
    )

    # Search Natural Persons
    natural_results = (
        db.query(models.NaturalPerson)
        .filter(
            or_(
                models.NaturalPerson.first_name.ilike(search_term),
                models.NaturalPerson.last_name.ilike(search_term),
                models.NaturalPerson.tax_id.ilike(search_term),
                models.NaturalPerson.nationality.ilike(search_term),
            )
        )
        .limit(limit)
        .all()
    )

    return {
        "legal_persons": [
            schemas.LegalPerson.from_orm(lp).dict() for lp in legal_results
        ],
        "natural_persons": [
            schemas.NaturalPerson.from_orm(np).dict() for np in natural_results
        ],
        "total": len(legal_results) + len(natural_results),
        "query": q,
        "tenant": tenant,
    }