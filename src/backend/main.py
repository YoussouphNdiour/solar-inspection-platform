"""Point d'entrée principal de l'application FastAPI."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import api_router
from config import settings
from database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Gestion du cycle de vie de l'application."""
    # Démarrage : appliquer les migrations Alembic (production)
    # ou create_all en dev si Alembic non disponible
    import os
    if os.environ.get("RUN_MIGRATIONS", "true").lower() == "true":
        try:
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
        except Exception:
            # Fallback dev local : create_all
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Arrêt : fermeture de la connexion
    await engine.dispose()


app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    description="API de gestion des inspections drone de centrales solaires",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict:
    """Endpoint de vérification de santé."""
    return {"status": "ok", "service": settings.project_name}
