from fastapi import FastAPI
from .routers import legal_persons, natural_persons, graph
from .database import engine, Base
from .routers import visualize  
app = FastAPI(title="Corporate Registry API")

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(legal_persons.router)
app.include_router(natural_persons.router)
app.include_router(graph.router)
app.include_router(visualize.router)  
@app.get("/")
def root():
    return {"message": "Corporate Registry API running"}