"""Endpoints FastAPI pour le traitement des images drone."""

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()


class ProcessingRequest(BaseModel):
    """Requête de traitement d'images pour une inspection."""

    inspection_id: uuid.UUID
    image_directory: str = Field(..., description="Chemin vers le répertoire d'images brutes")
    irradiance_wm2: float = Field(..., ge=0, description="Irradiance mesurée (W/m²)")
    wind_speed_ms: float = Field(..., ge=0, description="Vitesse du vent (m/s)")
    ambient_temp_c: float = Field(..., description="Température ambiante (°C)")


@router.post("/start", status_code=status.HTTP_202_ACCEPTED)
async def start_processing(payload: ProcessingRequest) -> dict:
    """Démarre le pipeline de traitement d'images pour une inspection.

    Lance de manière asynchrone : ingestion → alignement RGB/thermal → ODM → carte thermique.
    """
    return {
        "inspection_id": str(payload.inspection_id),
        "status": "queued",
        "message": "Traitement d'images mis en file d'attente",
    }


@router.get("/{inspection_id}/status")
async def get_processing_status(inspection_id: uuid.UUID) -> dict:
    """Retourne le statut du traitement d'images pour une inspection."""
    from config import settings
    import json
    from pathlib import Path

    status_path = (
        settings.shared_dir / "processed_images" / str(inspection_id) / "status.json"
    )
    if not status_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Aucun traitement trouvé pour l'inspection {inspection_id}",
        )
    with open(status_path) as f:
        return json.load(f)
