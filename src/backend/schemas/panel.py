"""Schémas Pydantic pour les panneaux photovoltaïques."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PanelCreate(BaseModel):
    """Données pour créer un panneau."""

    site_id: uuid.UUID
    string_id: str = Field(..., max_length=50, description="Identifiant de la string électrique")
    row_num: int = Field(..., ge=0, description="Numéro de rangée")
    position_num: int = Field(..., ge=0, description="Position dans la rangée")
    geometry: dict[str, Any] | None = Field(None, description="Polygone GeoJSON")


class PanelRead(BaseModel):
    """Réponse API pour un panneau."""

    id: uuid.UUID
    site_id: uuid.UUID
    string_id: str
    row_num: int
    position_num: int
    geometry: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}
