"""Point d'entrée principal de l'application FastAPI."""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import api_router
from config import settings
from database import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Gestion du cycle de vie de l'application.

    Le schéma est géré par Alembic (preDeployCommand dans render.yaml).
    Le lifespan ne tente aucune connexion DB au démarrage.
    """
    db_url = os.environ.get("DATABASE_URL", "NON DÉFINI — utilise défaut localhost!")
    logger.info("DATABASE_URL au démarrage : %s", db_url[:40] + "..." if len(db_url) > 40 else db_url)
    yield
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
    allow_origin_regex=r"https://.*\.onrender\.com",  # tous les services Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict:
    """Endpoint de vérification de santé."""
    return {"status": "ok", "service": settings.project_name}
