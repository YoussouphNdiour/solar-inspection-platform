"""Schémas Pydantic pour les sites de centrale solaire."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SiteCreate(BaseModel):
    """Données pour créer un site."""

    name: str = Field(..., min_length=1, max_length=255, description="Nom du site")
    location: dict[str, Any] = Field(..., description="Point GeoJSON {type: 'Point', coordinates: [lon, lat]}")
    surface_m2: float = Field(..., gt=0, description="Surface totale en m²")
    panel_count: int = Field(0, ge=0, description="Nombre total de panneaux")


class SiteUpdate(BaseModel):
    """Données pour modifier un site (champs optionnels)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    surface_m2: float | None = Field(None, gt=0)
    panel_count: int | None = Field(None, ge=0)


class SiteRead(BaseModel):
    """Réponse API pour un site."""

    id: uuid.UUID
    name: str
    location: dict[str, Any]
    surface_m2: float
    panel_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
