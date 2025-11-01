# File: schemas.py (updated)
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

class CountryProfileResponse(BaseModel):
    country: str = Field(..., alias="country")
    mandateStatus: str = Field(..., alias="mandate_status")
    archivingPeriod: str = Field(..., alias="archiving_period")
    scopeTriggersResidents: str = Field(..., alias="scope_triggers_residents")
    scopeTriggersNonResidentsWithVatId: str = Field(..., alias="scope_triggers_non_residents_with_vat_id")
    scopeTriggersLogic: str = Field(..., alias="scope_triggers_logic")
    scopeB2bStatus: str = Field(..., alias="scope_b2b_status")
    scopeB2bStartDate: str = Field(..., alias="scope_b2b_start_date")
    scopeB2bPosRelevant: str = Field(..., alias="scope_b2b_pos_relevant")
    scopeB2bStaggeredApplies: str = Field(..., alias="scope_b2b_staggered_applies")
    scopeB2bStaggeredThreshold: str = Field(..., alias="scope_b2b_staggered_threshold")
    scopeB2gStatus: str = Field(..., alias="scope_b2g_status")
    scopeB2gStartDate: str = Field(..., alias="scope_b2g_start_date")
    scopeB2gStaggeredApplies: str = Field(..., alias="scope_b2g_staggered_applies")
    scopeB2gStaggeredThreshold: str = Field(..., alias="scope_b2g_staggered_threshold")
    scopeB2cReportingObligation: str = Field(..., alias="scope_b2c_reporting_obligation")
    scopeB2cStartDate: str = Field(..., alias="scope_b2c_start_date")
    scopeBuyersChoiceApplies: str = Field(..., alias="scope_buyers_choice_applies")
    scopeBuyersChoiceCondition: str = Field(..., alias="scope_buyers_choice_condition")
    architectureModelType: str = Field(..., alias="architecture_model_type")
    architectureModelCornerModel: str = Field(..., alias="architecture_model_corner_model")
    architectureModelDescription: str = Field(..., alias="architecture_model_description")
    architectureFormatsEn16931Status: str = Field(..., alias="architecture_formats_en16931_status")
    architectureFormatsEn16931Version: str = Field(..., alias="architecture_formats_en16931_version")
    architectureFormatsNationalCiusApplies: str = Field(..., alias="architecture_formats_national_cius_applies")
    architectureFormatsNationalCiusSchemaName: str = Field(..., alias="architecture_formats_national_cius_schema_name")
    architectureFormatsAllowedSyntaxes: List[str] = Field(..., alias="architecture_formats_allowed_syntaxes")
    architectureFormatsPdfConform: str = Field(..., alias="architecture_formats_pdf_conform")
    architectureTransmissionPeppolStatus: str = Field(..., alias="architecture_transmission_peppol_status")
    reportingStatePlatformApplies: str = Field(..., alias="reporting_state_platform_applies")
    reportingStatePlatformName: str = Field(..., alias="reporting_state_platform_name")
    reportingStatePlatformMandatory: str = Field(..., alias="reporting_state_platform_mandatory")
    reportingClearanceRealTimeCtc: str = Field(..., alias="reporting_clearance_real_time_ctc")
    reportingClearanceValidityAfterRelease: str = Field(..., alias="reporting_clearance_validity_after_release")
    reportingReqDrr: str = Field(..., alias="reporting_req_drr")
    reportingReqRealTime: str = Field(..., alias="reporting_req_real_time")
    reportingReqFrequency: str = Field(..., alias="reporting_req_frequency")
    additionalSystemCert: str = Field(..., alias="additional_system_cert")
    additionalSaftObligation: str = Field(..., alias="additional_saft_obligation")
    additionalSaftSubmission: str = Field(..., alias="additional_saft_submission")
    additionalLocalIdsObligation: str = Field(..., alias="additional_local_ids_obligation")
    additionalLocalIdsType: str = Field(..., alias="additional_local_ids_type")
    additionalTransactionStatusReporting: str = Field(..., alias="additional_transaction_status_reporting")
    additionalSpecialNotes: str = Field(..., alias="additional_special_notes")
    additionalSanctions: str = Field(..., alias="additional_sanctions")

    @classmethod
    def from_orm(cls, obj):
        # Custom from_orm to reconstruct nested structure
        scope = {
            "triggers": {
                "residents": obj.scope_triggers_residents,
                "nonResidentsWithVatId": obj.scope_triggers_non_residents_with_vat_id,
                "logic": obj.scope_triggers_logic,
            },
            "b2b": {
                "status": obj.scope_b2b_status,
                "startDate": obj.scope_b2b_start_date,
                "posRelevant": obj.scope_b2b_pos_relevant,
                "staggered": {
                    "applies": obj.scope_b2b_staggered_applies,
                    "threshold": obj.scope_b2b_staggered_threshold,
                },
            },
            "b2g": {
                "status": obj.scope_b2g_status,
                "startDate": obj.scope_b2g_start_date,
                "staggered": {
                    "applies": obj.scope_b2g_staggered_applies,
                    "threshold": obj.scope_b2g_staggered_threshold,
                },
            },
            "b2c": {
                "reportingObligation": obj.scope_b2c_reporting_obligation,
                "startDate": obj.scope_b2c_start_date,
            },
            "buyersChoice": {
                "applies": obj.scope_buyers_choice_applies,
                "condition": obj.scope_buyers_choice_condition,
            },
        }
        architecture = {
            "model": {
                "type": obj.architecture_model_type,
                "cornerModel": obj.architecture_model_corner_model,
                "description": obj.architecture_model_description,
            },
            "formats": {
                "en16931": {
                    "status": obj.architecture_formats_en16931_status,
                    "version": obj.architecture_formats_en16931_version,
                },
                "nationalCius": {
                    "applies": obj.architecture_formats_national_cius_applies,
                    "schemaName": obj.architecture_formats_national_cius_schema_name,
                },
                "allowedSyntaxes": json.loads(obj.architecture_formats_allowed_syntaxes) if obj.architecture_formats_allowed_syntaxes else [],
                "pdfConform": obj.architecture_formats_pdf_conform,
            },
            "transmission": {
                "peppol": {
                    "status": obj.architecture_transmission_peppol_status,
                },
            },
        }
        reporting = {
            "statePlatform": {
                "applies": obj.reporting_state_platform_applies,
                "name": obj.reporting_state_platform_name,
                "mandatory": obj.reporting_state_platform_mandatory,
            },
            "clearance": {
                "realTimeCtc": obj.reporting_clearance_real_time_ctc,
                "validityAfterRelease": obj.reporting_clearance_validity_after_release,
            },
            "reportingReq": {
                "drr": obj.reporting_req_drr,
                "realTime": obj.reporting_req_real_time,
                "frequency": obj.reporting_req_frequency,
            },
        }
        additional = {
            "systemCert": obj.additional_system_cert,
            "saft": {
                "obligation": obj.additional_saft_obligation,
                "submission": obj.additional_saft_submission,
            },
            "localIds": {
                "obligation": obj.additional_local_ids_obligation,
                "type": obj.additional_local_ids_type,
            },
            "transactionStatusReporting": obj.additional_transaction_status_reporting,
            "specialNotes": obj.additional_special_notes,
            "sanctions": obj.additional_sanctions,
        }
        return cls(
            country=obj.country,
            mandateStatus=obj.mandate_status,
            archivingPeriod=obj.archiving_period,
            scope=scope,
            architecture=architecture,
            reporting=reporting,
            additional=additional
        )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True