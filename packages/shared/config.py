"""
Configuration module for ApplyForge
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "ApplyForge"
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./data/applyforge.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # AI & Match Settings
    AI_MATCH_ENABLED: bool = True
    SAFE_MODE: bool = True
    ZERO_SILENT_SUBMISSIONS: bool = True
    
    # Security
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production"
    LOG_LEVEL: str = "INFO"
    
    # Storage
    STORAGE_DIR: str = str(BASE_DIR / "data" / "storage")
    
    @property
    def storage_path(self) -> Path:
        p = Path(self.STORAGE_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
