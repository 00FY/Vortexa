import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Service Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # LLM Configuration
    LLM_PROVIDER: str = "mock"  # "mock", "openai", "anthropic", "groq"
    LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # ActionGate Integration
    ACTIONGATE_BASE_URL: str = "http://localhost:8001"
    ACTIONGATE_API_KEY: Optional[str] = "ag-secret-key-default"
    ACTIONGATE_TIMEOUT_SECONDS: float = 5.0
    
    # ERP Backend Integration
    ERP_BASE_URL: str = "http://localhost:8000"
    ERP_API_KEY: Optional[str] = "erp-secret-key-default"
    ERP_JWT_SECRET: str = "erp-jwt-secret-for-testing"
    ERP_TIMEOUT_SECONDS: float = 5.0
    
    # Mode flags
    USE_MOCKS: bool = True  # Automatically use high-fidelity mocks when external services are not reachable
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
