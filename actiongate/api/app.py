"""ActionGate FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from actiongate.api.routes import router

app = FastAPI(
    title="ActionGate Authorization Engine",
    description="Deterministic AI Agent Action Authorization Gateway with WARS risk scoring and tamper-evident auditing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
