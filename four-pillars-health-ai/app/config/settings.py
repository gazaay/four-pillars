import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, PostgresDsn, field_validator, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """
    Application settings loaded from environment variables
    """
    # API Configuration
    API_PREFIX: str = "/api"
    API_DEBUG: bool = os.getenv("API_DEBUG", "False").lower() in ("true", "1", "t")
    
    # Security and Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt_supersecretkey")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Database
    DATABASE_URL: PostgresDsn = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/healthai")
    DATABASE_MAX_CONNECTIONS: int = int(os.getenv("DATABASE_MAX_CONNECTIONS", "10"))
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # AI Model Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    DEFAULT_CHAT_MODEL: str = os.getenv("DEFAULT_CHAT_MODEL", "gpt-4-1106-preview")
    MEDICAL_ADVICE_MODEL: str = os.getenv("MEDICAL_ADVICE_MODEL", "gpt-4-1106-preview")
    POLICY_EXPERT_MODEL: str = os.getenv("POLICY_EXPERT_MODEL", "gpt-4-1106-preview")
    PATIENT_HISTORY_MODEL: str = os.getenv("PATIENT_HISTORY_MODEL", "gpt-4-1106-preview")
    
    # Model Specific Settings
    MODEL_TIMEOUT_SECONDS: int = int(os.getenv("MODEL_TIMEOUT_SECONDS", "30"))
    MAX_TOKENS_RESPONSE: int = int(os.getenv("MAX_TOKENS_RESPONSE", "2000"))
    
    # Health Expert System
    EXPERT_SYSTEM_TEMPERATURE: float = float(os.getenv("EXPERT_SYSTEM_TEMPERATURE", "0.3"))
    
    # Common model settings
    MODEL_SETTINGS: Dict[str, Any] = {
        "default": {
            "temperature": 0.7,
            "max_tokens": 1500,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        },
        "medical_advice": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "top_p": 0.95,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.1,
        },
        "policy_expert": {
            "temperature": 0.4,
            "max_tokens": 2000,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        },
        "patient_history": {
            "temperature": 0.2,
            "max_tokens": 1500,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }
    }

# Create a global instance of settings
settings = Settings() 