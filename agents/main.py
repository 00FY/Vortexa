from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.api.routes import router
from attacks.api import router as attacks_router

app = FastAPI(
    title="ActionGate AI Agent Orchestrator & Attack Lab",
    description="LangGraph AI agent orchestration backend connecting Mini ERP Chatbot to ActionGate",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(attacks_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agents.main:app", host="0.0.0.0", port=8002, reload=True)
