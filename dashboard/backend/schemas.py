# File: schemas.py (updated - add from_orm to CountryProfile and use it for response)
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import json

class RegulatoryFeed(BaseModel):
    """Pydantic model for regulatory feed items with validation."""
    date: str = Field(..., description="Date of the regulatory update, e.g., 'Oct 9, 2025'")
    country: str = Field(..., description="Country or location, e.g., 'USA'")
    content: str = Field(..., description="Description of the regulatory update")

class RegulatoryFeedResponse(BaseModel):
    date: str = Field(..., alias="date")
    country: str = Field(..., alias="country")
    content: str = Field(..., alias="content")

    class Config:
        from_attributes = True  # Allows mapping from SQLAlchemy models

class ClientProfileCreate(BaseModel):
    client_id: str
    company_name: str
    country: str
    new_regulation: str
    deadline: Optional[str] = None  # ISO format string
    status: str = "pending"

class ClientProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    country: Optional[str] = None
    new_regulation: Optional[str] = None
    deadline: Optional[str] = None  # ISO format string
    status: Optional[str] = None

class ClientProfileResponse(BaseModel):
    clientId: str = Field(..., alias="client_id")
    companyName: str = Field(..., alias="company_name")
    country: str = Field(..., alias="country")
    newRegulation: str = Field(..., alias="new_regulation")
    deadline: Optional[date] = Field(None, alias="deadline")  # Changed to date; auto-serializes to ISO str in JSON
    status: str = Field(..., alias="status")

    class Config:
        from_attributes = True  # Allows mapping from SQLAlchemy models

# Country Profile Schemas
class ScopeTriggers(BaseModel):
    residents: str
    nonResidentsWithVatId: str
    logic: str

class Staggered(BaseModel):
    applies: str
    threshold: str

class B2B(BaseModel):
    status: str
    startDate: str
    posRelevant: str
    staggered: Staggered

class B2G(BaseModel):
    status: str
    startDate: str
    staggered: Staggered

class B2C(BaseModel):
    reportingObligation: str
    startDate: str

class BuyersChoice(BaseModel):
    applies: str
    condition: str

class Scope(BaseModel):
    triggers: ScopeTriggers
    b2b: B2B
    b2g: B2G
    b2c: B2C
    buyersChoice: BuyersChoice

class Model(BaseModel):
    type: str
    cornerModel: str
    description: str

class EN16931(BaseModel):
    status: str
    version: str

class NationalCius(BaseModel):
    applies: str
    schemaName: str

class Formats(BaseModel):
    en16931: EN16931
    nationalCius: NationalCius
    allowedSyntaxes: List[str]
    pdfConform: str

class Peppol(BaseModel):
    status: str

class Transmission(BaseModel):
    peppol: Peppol

class Architecture(BaseModel):
    model: Model
    formats: Formats
    transmission: Transmission

class StatePlatform(BaseModel):
    applies: str
    name: str
    mandatory: str

class Clearance(BaseModel):
    realTimeCtc: str
    validityAfterRelease: str

class ReportingReq(BaseModel):
    drr: str
    realTime: str
    frequency: str

class Reporting(BaseModel):
    statePlatform: StatePlatform
    clearance: Clearance
    reportingReq: ReportingReq

class Saft(BaseModel):
    obligation: str
    submission: str

class LocalIds(BaseModel):
    obligation: str
    type: str

class Additional(BaseModel):
    systemCert: str
    saft: Saft
    localIds: LocalIds
    transactionStatusReporting: str
    specialNotes: str
    sanctions: str

class CountryProfile(BaseModel):
    country: str
    mandateStatus: str
    archivingPeriod: str
    scope: Scope
    architecture: Architecture
    reporting: Reporting
    additional: Additional

    @classmethod
    def from_orm(cls, obj):
        # Reconstruct nested structures from flat ORM attributes
        # Scope
        triggers = ScopeTriggers(
            residents=obj.scope_triggers_residents or '',
            nonResidentsWithVatId=obj.scope_triggers_non_residents_with_vat_id or '',
            logic=obj.scope_triggers_logic or ''
        )
        b2b_staggered = Staggered(
            applies=obj.scope_b2b_staggered_applies or '',
            threshold=obj.scope_b2b_staggered_threshold or ''
        )
        b2b = B2B(
            status=obj.scope_b2b_status or '',
            startDate=obj.scope_b2b_start_date or '',
            posRelevant=obj.scope_b2b_pos_relevant or '',
            staggered=b2b_staggered
        )
        b2g_staggered = Staggered(
            applies=obj.scope_b2g_staggered_applies or '',
            threshold=obj.scope_b2g_staggered_threshold or ''
        )
        b2g = B2G(
            status=obj.scope_b2g_status or '',
            startDate=obj.scope_b2g_start_date or '',
            staggered=b2g_staggered
        )
        b2c = B2C(
            reportingObligation=obj.scope_b2c_reporting_obligation or '',
            startDate=obj.scope_b2c_start_date or ''
        )
        buyers_choice = BuyersChoice(
            applies=obj.scope_buyers_choice_applies or '',
            condition=obj.scope_buyers_choice_condition or ''
        )
        scope = Scope(
            triggers=triggers,
            b2b=b2b,
            b2g=b2g,
            b2c=b2c,
            buyersChoice=buyers_choice
        )

        # Architecture
        model = Model(
            type=obj.architecture_model_type or '',
            cornerModel=obj.architecture_model_corner_model or '',
            description=obj.architecture_model_description or ''
        )
        en16931 = EN16931(
            status=obj.architecture_formats_en16931_status or '',
            version=obj.architecture_formats_en16931_version or ''
        )
        national_cius = NationalCius(
            applies=obj.architecture_formats_national_cius_applies or '',
            schemaName=obj.architecture_formats_national_cius_schema_name or ''
        )
        allowed_syntaxes = json.loads(obj.architecture_formats_allowed_syntaxes or '[]')
        formats = Formats(
            en16931=en16931,
            nationalCius=national_cius,
            allowedSyntaxes=allowed_syntaxes,
            pdfConform=obj.architecture_formats_pdf_conform or ''
        )
        peppol = Peppol(
            status=obj.architecture_transmission_peppol_status or ''
        )
        transmission = Transmission(
            peppol=peppol
        )
        architecture = Architecture(
            model=model,
            formats=formats,
            transmission=transmission
        )

        # Reporting
        state_platform = StatePlatform(
            applies=obj.reporting_state_platform_applies or '',
            name=obj.reporting_state_platform_name or '',
            mandatory=obj.reporting_state_platform_mandatory or ''
        )
        clearance = Clearance(
            realTimeCtc=obj.reporting_clearance_real_time_ctc or '',
            validityAfterRelease=obj.reporting_clearance_validity_after_release or ''
        )
        reporting_req = ReportingReq(
            drr=obj.reporting_req_drr or '',
            realTime=obj.reporting_req_real_time or '',
            frequency=obj.reporting_req_frequency or ''
        )
        reporting = Reporting(
            statePlatform=state_platform,
            clearance=clearance,
            reportingReq=reporting_req
        )

        # Additional
        saft = Saft(
            obligation=obj.additional_saft_obligation or '',
            submission=obj.additional_saft_submission or ''
        )
        local_ids = LocalIds(
            obligation=obj.additional_local_ids_obligation or '',
            type=obj.additional_local_ids_type or ''
        )
        additional = Additional(
            systemCert=obj.additional_system_cert or '',
            saft=saft,
            localIds=local_ids,
            transactionStatusReporting=obj.additional_transaction_status_reporting or '',
            specialNotes=obj.additional_special_notes or '',
            sanctions=obj.additional_sanctions or ''
        )

        return cls(
            country=obj.country or '',
            mandateStatus=obj.mandate_status or '',
            archivingPeriod=obj.archiving_period or '',
            scope=scope,
            architecture=architecture,
            reporting=reporting,
            additional=additional
        )