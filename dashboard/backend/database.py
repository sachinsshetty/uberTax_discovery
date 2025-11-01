# File: database.py (updated)
import os
import json
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum as SQLEnum, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from datetime import date
from constants import MOCK_DATA_JSON, COUNTRY_PROFILES_JSON, REGULATORY_FEED_JSON
from enum import Enum
logger = logging.getLogger(__name__)

# Define Status Enum for consistency
class StatusEnum(str, Enum):
    PENDING = "pending"
    LIVE = "LIVE"
    MONITORED = "MONITORED"
    # Add other statuses as needed, e.g., COMPLETED = "completed", EXPIRED = "expired"

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "app.db")
db_dir = Path(SQLITE_DB_PATH).parent
db_dir.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, index=True)  # Added unique=True for integrity
    company_name = Column(String)
    country = Column(String)
    new_regulation = Column(String)
    deadline = Column(Date)
    status = Column(SQLEnum(StatusEnum, name="client_status"), default=StatusEnum.PENDING)  # Use Enum with default

class RegulatoryFeed(Base):
    __tablename__ = "regulatory_feed"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    country = Column(String, nullable=False)
    content = Column(String, nullable=False)

class CountryProfile(Base):
    __tablename__ = "country_profiles"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, unique=True, nullable=False, index=True)
    mandate_status = Column(String)
    archiving_period = Column(String)
    scope_triggers_residents = Column(String)
    scope_triggers_non_residents_with_vat_id = Column(String)
    scope_triggers_logic = Column(String)
    scope_b2b_status = Column(String)
    scope_b2b_start_date = Column(String)
    scope_b2b_pos_relevant = Column(String)
    scope_b2b_staggered_applies = Column(String)
    scope_b2b_staggered_threshold = Column(String)
    scope_b2g_status = Column(String)
    scope_b2g_start_date = Column(String)
    scope_b2g_staggered_applies = Column(String)
    scope_b2g_staggered_threshold = Column(String)
    scope_b2c_reporting_obligation = Column(String)
    scope_b2c_start_date = Column(String)
    scope_buyers_choice_applies = Column(String)
    scope_buyers_choice_condition = Column(String)
    architecture_model_type = Column(String)
    architecture_model_corner_model = Column(String)
    architecture_model_description = Column(String)
    architecture_formats_en16931_status = Column(String)
    architecture_formats_en16931_version = Column(String)
    architecture_formats_national_cius_applies = Column(String)
    architecture_formats_national_cius_schema_name = Column(String)
    architecture_formats_allowed_syntaxes = Column(String)  # JSON string for array
    architecture_formats_pdf_conform = Column(String)
    architecture_transmission_peppol_status = Column(String)
    reporting_state_platform_applies = Column(String)
    reporting_state_platform_name = Column(String)
    reporting_state_platform_mandatory = Column(String)
    reporting_clearance_real_time_ctc = Column(String)
    reporting_clearance_validity_after_release = Column(String)
    reporting_req_drr = Column(String)
    reporting_req_real_time = Column(String)
    reporting_req_frequency = Column(String)
    additional_system_cert = Column(String)
    additional_saft_obligation = Column(String)
    additional_saft_submission = Column(String)
    additional_local_ids_obligation = Column(String)
    additional_local_ids_type = Column(String)
    additional_transaction_status_reporting = Column(String)
    additional_special_notes = Column(String)
    additional_sanctions = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def startup_event():
    db = SessionLocal()
    try:
        # Handle ClientProfile mock data insertion
        if db.query(ClientProfile).count() == 0:
            if not MOCK_DATA_JSON.exists():
                logger.warning(f"Mock data JSON file not found at {MOCK_DATA_JSON}. Skipping mock data insertion.")
            else:
                try:
                    with open(MOCK_DATA_JSON, 'r', encoding='utf-8') as jsonfile:
                        mock_data = json.load(jsonfile)
                    
                    logger.info(f"Loaded {len(mock_data)} client profiles from JSON.")
                except Exception as e:
                    logger.error(f"Failed to load mock data JSON: {str(e)}. Skipping mock data insertion.")
                    mock_data = []

                for data in mock_data:
                    # Check for duplicates before adding
                    if db.query(ClientProfile).filter(ClientProfile.client_id == data["client_id"]).first():
                        logger.info(f"Skipping existing client {data['client_id']}.")
                        continue
                    
                    parsed_data = data.copy()
                    if data["deadline"] and isinstance(data["deadline"], str) and data["deadline"].strip():
                        try:
                            parsed_data["deadline"] = date.fromisoformat(data["deadline"].strip())
                        except ValueError:
                            logger.warning(f"Invalid deadline format '{data['deadline']}' for client {data['client_id']}. Setting to None.")
                            parsed_data["deadline"] = None
                    else:
                        parsed_data["deadline"] = None
                    
                    # Map string status to Enum
                    try:
                        parsed_data["status"] = StatusEnum(parsed_data["status"])
                    except ValueError:
                        logger.warning(f"Invalid status '{parsed_data['status']}' for client {data['client_id']}. Setting to PENDING.")
                        parsed_data["status"] = StatusEnum.PENDING
                    
                    client = ClientProfile(**parsed_data)
                    db.add(client)
                db.commit()
                logger.info("Mock data inserted successfully.")

        # Handle RegulatoryFeed mock data insertion
        if db.query(RegulatoryFeed).count() == 0:
            if not REGULATORY_FEED_JSON.exists():
                logger.warning(f"Regulatory feed JSON file not found at {REGULATORY_FEED_JSON}. Skipping regulatory feed data insertion.")
            else:
                try:
                    with open(REGULATORY_FEED_JSON, 'r', encoding='utf-8') as jsonfile:
                        feed_data = json.load(jsonfile)
                    
                    logger.info(f"Loaded {len(feed_data)} regulatory feed items from JSON.")
                except Exception as e:
                    logger.error(f"Failed to load regulatory feed JSON: {str(e)}. Skipping regulatory feed data insertion.")
                    feed_data = []

                for data in feed_data:
                    # Optional: Check for duplicates, e.g., by unique combination of date and country if needed
                    # For now, insert all as they might not have unique constraints beyond id
                    feed_item = RegulatoryFeed(**data)
                    db.add(feed_item)
                db.commit()
                logger.info(f"Inserted {len(feed_data)} regulatory feed items.")

        # Handle CountryProfile mock data insertion
        if db.query(CountryProfile).count() == 0:
            if not COUNTRY_PROFILES_JSON.exists():
                logger.warning(f"Country profiles JSON file not found at {COUNTRY_PROFILES_JSON}. Skipping country profiles data insertion.")
            else:
                try:
                    with open(COUNTRY_PROFILES_JSON, 'r', encoding='utf-8') as jsonfile:
                        country_data = json.load(jsonfile)
                    
                    logger.info(f"Loaded {len(country_data)} country profiles from JSON.")
                except Exception as e:
                    logger.error(f"Failed to load country profiles JSON: {str(e)}. Skipping country profiles data insertion.")
                    country_data = []

                for data in country_data:
                    # Check for duplicates by country
                    if db.query(CountryProfile).filter(CountryProfile.country == data["country"]).first():
                        logger.info(f"Skipping existing country profile {data['country']}.")
                        continue
                    
                    # Flatten nested structure to flat columns
                    flattened = {
                        "country": data["country"],
                        "mandate_status": data["mandateStatus"],
                        "archiving_period": data["archivingPeriod"],
                        # Scope triggers
                        "scope_triggers_residents": data["scope"]["triggers"]["residents"],
                        "scope_triggers_non_residents_with_vat_id": data["scope"]["triggers"]["nonResidentsWithVatId"],
                        "scope_triggers_logic": data["scope"]["triggers"]["logic"],
                        # Scope B2B
                        "scope_b2b_status": data["scope"]["b2b"]["status"],
                        "scope_b2b_start_date": data["scope"]["b2b"]["startDate"],
                        "scope_b2b_pos_relevant": data["scope"]["b2b"]["posRelevant"],
                        "scope_b2b_staggered_applies": data["scope"]["b2b"]["staggered"]["applies"],
                        "scope_b2b_staggered_threshold": data["scope"]["b2b"]["staggered"]["threshold"],
                        # Scope B2G
                        "scope_b2g_status": data["scope"]["b2g"]["status"],
                        "scope_b2g_start_date": data["scope"]["b2g"]["startDate"],
                        "scope_b2g_staggered_applies": data["scope"]["b2g"]["staggered"]["applies"],
                        "scope_b2g_staggered_threshold": data["scope"]["b2g"]["staggered"]["threshold"],
                        # Scope B2C
                        "scope_b2c_reporting_obligation": data["scope"]["b2c"]["reportingObligation"],
                        "scope_b2c_start_date": data["scope"]["b2c"]["startDate"],
                        # Scope buyersChoice
                        "scope_buyers_choice_applies": data["scope"]["buyersChoice"]["applies"],
                        "scope_buyers_choice_condition": data["scope"]["buyersChoice"]["condition"],
                        # Architecture model
                        "architecture_model_type": data["architecture"]["model"]["type"],
                        "architecture_model_corner_model": data["architecture"]["model"]["cornerModel"],
                        "architecture_model_description": data["architecture"]["model"]["description"],
                        # Architecture formats
                        "architecture_formats_en16931_status": data["architecture"]["formats"]["en16931"]["status"],
                        "architecture_formats_en16931_version": data["architecture"]["formats"]["en16931"]["version"],
                        "architecture_formats_national_cius_applies": data["architecture"]["formats"]["nationalCius"]["applies"],
                        "architecture_formats_national_cius_schema_name": data["architecture"]["formats"]["nationalCius"]["schemaName"],
                        "architecture_formats_allowed_syntaxes": json.dumps(data["architecture"]["formats"]["allowedSyntaxes"]),
                        "architecture_formats_pdf_conform": data["architecture"]["formats"]["pdfConform"],
                        # Architecture transmission
                        "architecture_transmission_peppol_status": data["architecture"]["transmission"]["peppol"]["status"],
                        # Reporting statePlatform
                        "reporting_state_platform_applies": data["reporting"]["statePlatform"]["applies"],
                        "reporting_state_platform_name": data["reporting"]["statePlatform"]["name"],
                        "reporting_state_platform_mandatory": data["reporting"]["statePlatform"]["mandatory"],
                        # Reporting clearance
                        "reporting_clearance_real_time_ctc": data["reporting"]["clearance"]["realTimeCtc"],
                        "reporting_clearance_validity_after_release": data["reporting"]["clearance"]["validityAfterRelease"],
                        # Reporting req
                        "reporting_req_drr": data["reporting"]["reportingReq"]["drr"],
                        "reporting_req_real_time": data["reporting"]["reportingReq"]["realTime"],
                        "reporting_req_frequency": data["reporting"]["reportingReq"]["frequency"],
                        # Additional
                        "additional_system_cert": data["additional"]["systemCert"],
                        "additional_saft_obligation": data["additional"]["saft"]["obligation"],
                        "additional_saft_submission": data["additional"]["saft"]["submission"],
                        "additional_local_ids_obligation": data["additional"]["localIds"]["obligation"],
                        "additional_local_ids_type": data["additional"]["localIds"]["type"],
                        "additional_transaction_status_reporting": data["additional"]["transactionStatusReporting"],
                        "additional_special_notes": data["additional"]["specialNotes"],
                        "additional_sanctions": data["additional"]["sanctions"],
                    }
                    
                    profile = CountryProfile(**flattened)
                    db.add(profile)
                db.commit()
                logger.info("Country profiles data inserted successfully.")
    finally:
        db.close()