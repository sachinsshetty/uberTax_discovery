from fastapi import FastAPI
from api.v1 import legal_persons #, natural_persons, graph
#from app.core.tenant_middleware import tenant_middleware
#from app.core.database import engine
#from app.models import Base
import asyncio

app = FastAPI(title="Corporate Registry API")

#app.add_middleware(tenant_middleware)

app.include_router(legal_persons.router, prefix="/legal_persons")
#app.include_router(natural_persons.router, prefix="/natural_persons")
#app.include_router(graph.router, prefix="/graph")

'''
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Ensure common schema exists
        await conn.execute("CREATE SCHEMA IF NOT EXISTS common")
        await conn.run_sync(Base.metadata.create_all)  # creates tables in current schema
'''