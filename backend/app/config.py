"""Application settings, loaded from environment variables / backend/.env."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", env_ignore_empty=True, extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    ai_provider: str = "auto"  # auto | openai | gemini | mock

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    notification_email: str = ""
    notification_mode: str = "auto"  # auto | email | mock

    database_url: str = "sqlite:///./data/applyforge.db"
    resume_dir: str = "./resumes"

    application_connector: str = "mock"  # mock | playwright
    browser_headless: bool = True
    match_threshold: int = 75
    max_upload_mb: int = 5
    cors_origins: str = "http://localhost:5173"
    allow_local_urls: bool = False
    max_applications_per_run: int = 10

    @property
    def sqlalchemy_url(self) -> str:
        """Resolve relative sqlite paths against the repo root so cwd does not matter."""
        prefix = "sqlite:///./"
        if self.database_url.startswith(prefix):
            return f"sqlite:///{ROOT_DIR / self.database_url[len(prefix):]}"
        return self.database_url

    @property
    def resume_path(self) -> Path:
        p = Path(self.resume_dir)
        return p if p.is_absolute() else (ROOT_DIR / p).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
