"""Schémas Pydantic pour les inspections."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from models.inspection import InspectionStatus


class InspectionCreate(BaseModel):
    """Données pour créer une inspection."""

    site_id: uuid.UUID = Field(..., description="Identifiant du site à inspecter")
    drone_id: uuid.UUID | None = Field(None, description="Drone assigné")
    irradiance_wm2: float | None = Field(None, ge=0, description="Irradiance solaire mesurée (W/m²)")
    wind_speed_ms: float | None = Field(None, ge=0, description="Vitesse du vent (m/s)")
    ambient_temp_c: float | None = Field(None, description="Température ambiante (°C)")


class InspectionStatusUpdate(BaseModel):
    """Mise à jour du statut d'une inspection."""

    status: InspectionStatus = Field(..., description="Nouveau statut")


class InspectionRead(BaseModel):
    """Réponse API pour une inspection."""

    id: uuid.UUID
    site_id: uuid.UUID
    drone_id: uuid.UUID | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    irradiance_wm2: float | None
    wind_speed_ms: float | None
    ambient_temp_c: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
