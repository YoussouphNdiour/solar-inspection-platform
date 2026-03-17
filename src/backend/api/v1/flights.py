"""Endpoints FastAPI pour la génération et validation des plans de vol."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from flight.planner import FlightPlanner
from flight.validators import FlightPlanValidator
from models.drone import DroneModel
from models.site import Site

router = APIRouter()


class FlightPlanRequest(BaseModel):
    """Paramètres pour générer un plan de vol."""

    site_id: uuid.UUID
    drone_model: DroneModel
    target_gsd_rgb_cm: float = Field(2.5, ge=1.0, le=10.0, description="GSD cible RGB en cm/px")
    target_gsd_thermal_cm: float = Field(7.0, ge=3.0, le=20.0, description="GSD cible thermique en cm/px")


@router.post("/plan", status_code=status.HTTP_200_OK)
async def generate_flight_plan(
    payload: FlightPlanRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Génère un plan de vol optimisé pour un site et un drone donnés."""
    result = await db.execute(select(Site).where(Site.id == payload.site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site {payload.site_id} introuvable")

    planner = FlightPlanner()
    plan = planner.generate(
        site_id=str(payload.site_id),
        surface_m2=site.surface_m2,
        drone_model=payload.drone_model,
        target_gsd_rgb_cm=payload.target_gsd_rgb_cm,
        target_gsd_thermal_cm=payload.target_gsd_thermal_cm,
    )
    return plan


@router.get("/{site_id}/latest")
async def get_latest_flight_plan(
    site_id: uuid.UUID,
) -> dict:
    """Retourne le dernier plan de vol généré pour un site."""
    from config import settings
    import json
    from pathlib import Path

    plan_dir = settings.shared_dir / "flight_plans" / str(site_id)
    plan_files = sorted(plan_dir.glob("*.json"), reverse=True) if plan_dir.exists() else []

    if not plan_files:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun plan de vol trouvé pour le site {site_id}",
        )

    with open(plan_files[0]) as f:
        return json.load(f)


@router.post("/{site_id}/validate")
async def validate_flight_plan(
    site_id: uuid.UUID,
    plan: dict,
) -> dict:
    """Valide un plan de vol selon les contraintes réglementaires."""
    validator = FlightPlanValidator()
    is_valid, errors = validator.validate(plan)
    return {
        "valid": is_valid,
        "errors": errors,
        "site_id": str(site_id),
    }
