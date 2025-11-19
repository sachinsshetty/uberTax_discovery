# app/middleware.py
import re
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from .database import tenant_context, base_engine
from sqlalchemy import text
from typing import Optional

# Regex for safe schema names
SAFE_TENANT_REGEX = re.compile(r"^[a-z0-9][a-z0-9_-]{0,61}[a-z0-9]$")


def get_tenant_from_request(request: Request) -> Optional[str]:
    """
    Extract tenant identifier from:
    1. Subdomain (acme.api.example.com → acme)
    2. X-Tenant header
    3. tenant query param (debug only)
    Priority: subdomain > header > query
    """
    # 1. Subdomain (recommended for production)
    host = request.headers.get("host", "")
    if "." in host:
        parts = host.split(".")
        subdomain = parts[0].lower()
        if subdomain and subdomain not in {"www", "api", "localhost", "127"}:
            if SAFE_TENANT_REGEX.match(subdomain):
                return subdomain

    # 2. Header fallback
    tenant_from_header = request.headers.get("X-Tenant")
    if tenant_from_header and SAFE_TENANT_REGEX.match(tenant_from_header.lower()):
        return tenant_from_header.lower()

    # 3. Query param (only in dev)
    tenant_from_query = request.query_params.get("tenant")
    if tenant_from_query and request.app.state.ENV == "development":
        if SAFE_TENANT_REGEX.match(tenant_from_query.lower()):
            return tenant_from_query.lower()

    return None


async def tenant_middleware(request: Request, call_next):
    """
    Main tenant middleware.
    Sets the correct PostgreSQL schema for the entire request.
    """
    if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path.startswith("/openapi.json") or request.url.path.startswith("/admin/tenants"):
        # Skip tenant check for Swagger/UI
        return await call_next(request)

    tenant_id = get_tenant_from_request(request)
    if not tenant_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Tenant not specified. Use subdomain (acme.yourapi.com), X-Tenant header, or ?tenant= param (dev only)."
            }
        )

    schema_name = f"tenant_{tenant_id}"

    # Verify tenant exists in public.tenants
    try:
        with base_engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM public.tenants WHERE schema_name = :schema"),
                {"schema": schema_name}
            ).fetchone()

            if not result:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"detail": f"Tenant '{tenant_id}' not found or not activated."}
                )

            # Verify schema actually exists in PostgreSQL
            schema_exists = conn.execute(
                text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema"),
                {"schema": schema_name}
            ).fetchone()

            if not schema_exists:
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={"detail": f"Tenant '{tenant_id}' is registered but schema missing. Contact admin."}
                )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Tenant resolution failed", "error": str(e)}
        )

    # Set tenant context + request.state for logging/dependencies
    request.state.tenant = tenant_id
    request.state.schema = schema_name

    with tenant_context(schema_name):
        response = await call_next(request)

    return response