from fastapi import FastAPI
from sqlalchemy import text

from backend.database.connection import engine
from backend.database.base import Base

import backend.models

from backend.models.assignment import Assignment

from backend.api.trucks import router as trucks_router
from backend.api.shipments import router as shipments_router
from backend.api.truck_locations import router as locations_router
from backend.api.backhaul import router as backhaul_router
from backend.api.assignments import router as assignments_router
from backend.api import demand_prediction
from backend.api import waiting_time_prediction
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Fleet Optimizer",
    description="AI-based fleet and backhaul optimization system",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(trucks_router)
app.include_router(shipments_router)
app.include_router(locations_router)
app.include_router(backhaul_router)
app.include_router(assignments_router)
app.include_router(demand_prediction.router)
app.include_router(waiting_time_prediction.router)

@app.get("/")
def root():
    return {
        "project": "AI Fleet Optimizer",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.get("/database-test")
def database_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "database": "connected",
        "test_result": value
    }