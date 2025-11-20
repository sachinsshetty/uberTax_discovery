# app/base.py
from sqlalchemy.ext.declarative import declarative_base

# This Base is shared by ALL tenant schemas
# It defines table structure only — no engine binding
Base = declarative_base()

# Optional: nice naming convention for constraints (recommended)
Base.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}