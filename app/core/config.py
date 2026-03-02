"""Centralized configuration using Pydantic Settings.

All environment variables are loaded from .env. No os.getenv() elsewhere.
"""

from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure .env is loaded for submodules (e.g. pipeline) that use os.getenv
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from .env."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = Field(default="SHL Recommendation API", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: Literal["dev", "staging", "prod"] = Field(
        default="dev", alias="ENVIRONMENT"
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./recommendation_engine.db",
        alias="DATABASE_URL",
    )

    # SHL Recommendation Engine (paths relative to project root)
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent,
        alias="PROJECT_ROOT",
    )
    shl_module_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
        / "shl_recommendation_system",
        alias="SHL_MODULE_PATH",
    )

    # GenAI / LLM
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")

    @property
    def use_llm(self) -> bool:
        """Whether to use LLM for query understanding."""
        return bool(self.gemini_api_key)


settings = Settings()
