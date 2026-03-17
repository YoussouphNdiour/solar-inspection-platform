"""Schémas Pydantic pour les drones."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from models.drone import DroneModel, DroneStatus


class DroneCreate(BaseModel):
    """Données pour enregistrer un drone."""

    model: DroneModel = Field(..., description="Modèle de drone DJI")
    serial_number: str = Field(..., min_length=1, max_length=100, description="Numéro de série")
    status: DroneStatus = Field(DroneStatus.AVAILABLE, description="Statut opérationnel")


class DroneRead(BaseModel):
    """Réponse API pour un drone."""

    id: uuid.UUID
    model: str
    serial_number: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
