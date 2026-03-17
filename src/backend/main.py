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
    """Gestion du cycle de vie de l'application.

    Utilise create_all au démarrage (simple et compatible async).
    Les migrations Alembic sont lancées via le preDeployCommand dans render.yaml.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict:
    """Endpoint de vérification de santé."""
    return {"status": "ok", "service": settings.project_name}
