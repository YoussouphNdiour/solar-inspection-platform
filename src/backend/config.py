"""Configuration de l'application via variables d'environnement."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Paramètres globaux de l'application."""

    database_url: str = "postgresql+asyncpg://solar:solar_dev_pwd@localhost:5432/solar_inspection"
    redis_url: str = "redis://localhost:6379"
    shared_dir: Path = Path("shared")
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Solar Inspection Platform"

    # URL du frontend — injectée par Render Blueprint ou définie manuellement
    frontend_url: str = "http://localhost:5173"

    # Sur Render, DATABASE_URL commence par "postgres://" — asyncpg veut "postgresql+asyncpg://"
    @property
    def async_database_url(self) -> str:
        """Normalise l'URL de base de données pour asyncpg."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def cors_origins(self) -> list[str]:
        """Origines CORS autorisées (local + Render)."""
        return [
            "http://localhost:5173",
            "http://localhost:3000",
            self.frontend_url,
        ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
