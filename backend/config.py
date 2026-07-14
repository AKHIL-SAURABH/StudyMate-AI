"""
StudyMate AI — Configuration Management.

Centralized configuration loaded from environment variables with
sensible defaults. Uses pydantic-settings for validation.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file and environment variables."""

    # ── Groq API ──────────────────────────────────────────────
    groq_api_key: str = ""

    # ── LLM Configuration ─────────────────────────────────────
    llm_primary_model: str = "llama-3.3-70b-versatile"
    llm_fallback_model: str = "qwen/qwen3-32b"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096

    # ── FastAPI ───────────────────────────────────────────────
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_debug: bool = True

    # ── Database ──────────────────────────────────────────────
    database_path: str = "data/studymate.db"

    # ── Agent ─────────────────────────────────────────────────
    agent_max_iterations: int = 5
    agent_memory_window: int = 20

    # ── Logging ───────────────────────────────────────────────
    log_level: str = "INFO"

    # ── Paths ─────────────────────────────────────────────────
    project_root: str = str(Path(__file__).resolve().parent.parent)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def database_url(self) -> str:
        """Absolute path to the SQLite database file."""
        db_path = Path(self.project_root) / self.database_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return str(db_path)

    @property
    def mcp_server_path(self) -> str:
        """Path to the MCP server entry script."""
        return str(Path(self.project_root) / "mcp_server" / "server.py")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Singleton Settings instance.
    """
    return Settings()
