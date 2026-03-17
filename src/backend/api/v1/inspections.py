"""Endpoints FastAPI pour la gestion des inspections."""

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.inspection import Inspection, InspectionStatus
from schemas.inspection import InspectionCreate, InspectionRead, InspectionStatusUpdate

router = APIRouter()


@router.get("/", response_model=list[InspectionRead])
async def list_inspections(
    site_id: uuid.UUID | None = Query(None, description="Filtrer par site"),
    status_filter: InspectionStatus | None = Query(None, alias="status", description="Filtrer par statut"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[InspectionRead]:
    """Retourne la liste des inspections, filtrables par site et statut."""
    query = select(Inspection)
    if site_id:
        query = query.where(Inspection.site_id == site_id)
    if status_filter:
        query = query.where(Inspection.status == status_filter)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    inspections = result.scalars().all()
    return [InspectionRead.model_validate(i) for i in inspections]


@router.post("/", response_model=InspectionRead, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    payload: InspectionCreate,
    db: AsyncSession = Depends(get_db),
) -> InspectionRead:
    """Crée une nouvelle inspection pour un site."""
    inspection = Inspection(
        site_id=payload.site_id,
        drone_id=payload.drone_id,
        status=InspectionStatus.PLANNED,
        irradiance_wm2=payload.irradiance_wm2,
        wind_speed_ms=payload.wind_speed_ms,
        ambient_temp_c=payload.ambient_temp_c,
    )
    db.add(inspection)
    await db.flush()
    await db.refresh(inspection)
    return InspectionRead.model_validate(inspection)


@router.get("/{inspection_id}", response_model=InspectionRead)
async def get_inspection(
    inspection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> InspectionRead:
    """Retourne les détails d'une inspection."""
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()
    if inspection is None:
        raise HTTPException(status_code=404, detail=f"Inspection {inspection_id} introuvable")
    return InspectionRead.model_validate(inspection)


@router.patch("/{inspection_id}/status", response_model=InspectionRead)
async def update_inspection_status(
    inspection_id: uuid.UUID,
    payload: InspectionStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> InspectionRead:
    """Change le statut d'une inspection."""
    from datetime import datetime, timezone

    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()
    if inspection is None:
        raise HTTPException(status_code=404, detail=f"Inspection {inspection_id} introuvable")

    inspection.status = payload.status
    if payload.status == InspectionStatus.IN_PROGRESS and inspection.started_at is None:
        inspection.started_at = datetime.now(timezone.utc)
    elif payload.status in (InspectionStatus.COMPLETED, InspectionStatus.FAILED):
        inspection.completed_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(inspection)
    return InspectionRead.model_validate(inspection)


@router.get("/{inspection_id}/anomalies")
async def get_inspection_anomalies(
    inspection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Retourne le GeoJSON des anomalies détectées pour une inspection.

    Priorité : colonne DB (Render) → fichier shared/ (local dev).
    """
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()
    if inspection is None:
        raise HTTPException(status_code=404, detail=f"Inspection {inspection_id} introuvable")

    # 1. Lire depuis la base de données (Render / production)
    if inspection.anomalies_geojson:
        return inspection.anomalies_geojson

    # 2. Fallback : lire depuis le filesystem (dev local avec shared/)
    geojson_path = settings.shared_dir / "anomalies" / str(inspection_id) / "anomalies.geojson"
    if geojson_path.exists():
        with open(geojson_path) as f:
            return json.load(f)

    raise HTTPException(
        status_code=404,
        detail=f"Aucune anomalie trouvée pour l'inspection {inspection_id}. "
               "Le pipeline de détection n'a pas encore été exécuté.",
    )


@router.put("/{inspection_id}/anomalies")
async def upload_inspection_anomalies(
    inspection_id: uuid.UUID,
    geojson: dict,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Stocke le GeoJSON des anomalies en base de données (Render-compatible)."""
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()
    if inspection is None:
        raise HTTPException(status_code=404, detail=f"Inspection {inspection_id} introuvable")

    inspection.anomalies_geojson = geojson
    await db.flush()
    return {"status": "stored", "inspection_id": str(inspection_id)}
