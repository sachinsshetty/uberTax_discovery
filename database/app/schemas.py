# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ====================== LEGAL PERSON ======================
class LegalPersonBase(BaseModel):
    name: str = Field(..., example="Acme Corp Ltd")
    registration_number: str = Field(..., example="12345678")
    jurisdiction: Optional[str] = None
    incorporation_date: Optional[str] = None
    status: Optional[str] = "active"


class LegalPersonCreate(LegalPersonBase):
    pass


class LegalPersonUpdate(BaseModel):          # ← WAS MISSING!
    name: Optional[str] = None
    registration_number: Optional[str] = None
    jurisdiction: Optional[str] = None
    incorporation_date: Optional[str] = None
    status: Optional[str] = None


class LegalPerson(LegalPersonBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ====================== NATURAL PERSON ======================
class NaturalPersonBase(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    tax_id: Optional[str] = None


class NaturalPersonCreate(NaturalPersonBase):
    pass


class NaturalPersonUpdate(BaseModel):         # ← WAS MISSING!
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    tax_id: Optional[str] = None


class NaturalPerson(NaturalPersonBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ====================== GRAPH SCHEMAS ======================
class ConnectionCreate(BaseModel):
    from_type: Literal["legal", "natural"]
    from_id: int
    to_type: Literal["legal", "natural"]
    to_id: int
    relation: str = Field(..., example="shareholder")
    share_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Shareholding percentage (0-100)"
    )


class ConnectionResponse(BaseModel):
    id: int
    from_type: str
    from_id: int
    to_type: str
    to_id: int
    relation: str
    share_percentage: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}