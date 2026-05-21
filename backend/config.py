"""
Configuration settings for the AI CRM HCP Module
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "AI CRM HCP Module"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./crm.db"
    # Alternative for PostgreSQL:
    # DATABASE_URL: str = "postgresql://user:password@localhost/ai_crm"
    # Alternative for MySQL:
    # DATABASE_URL: str = "mysql://user:password@localhost/ai_crm"
    
    # Groq Configuration
    # Make it non-required so the app can start and show a clear error later if missing.
    GROQ_API_KEY: str = ""
    # Use a supported Groq model by default.
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # AI Agent Configuration
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    # CORS Configuration
    # pydantic-settings expects JSON for complex types coming from env/.env.
    # If you set ALLOWED_ORIGINS in .env, format it as a JSON array string.
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        env_file = Path(__file__).resolve().parent / ".env"
        case_sensitive = True


DECOMMISSIONED_GROQ_MODELS = {
    "gemma2-9b-it": "llama-3.3-70b-versatile",
    "gemma2-9b": "llama-3.3-70b-versatile",
    "gemma2-3b": "llama-3.3-70b-versatile",
}

settings = Settings()
if settings.GROQ_MODEL.strip() in DECOMMISSIONED_GROQ_MODELS:
    settings.GROQ_MODEL = DECOMMISSIONED_GROQ_MODELS[settings.GROQ_MODEL.strip()]
