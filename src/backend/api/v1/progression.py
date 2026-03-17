"""Endpoints de progression des examens d'inspection."""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.inspection import Inspection, InspectionStatus

router = APIRouter(prefix="/inspections", tags=["progression"])

STEP_LABELS = [
    {"step": 0, "label": "Paiement", "icon": "💳"},
    {"step": 1, "label": "Téléchargement", "icon": "⬆️"},
    {"step": 2, "label": "Évaluation", "icon": "👁️"},
    {"step": 3, "label": "Analyse", "icon": "📊"},
    {"step": 4, "label": "Rapport", "icon": "📄"},
]


@router.get("/{inspection_id}/progress")
async def get_progress(inspection_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retourne la progression actuelle de l'inspection.

    Args:
        inspection_id: UUID de l'inspection.
        db: Session async SQLAlchemy.

    Returns:
        Dictionnaire avec progression, statut, pourcentage et étapes.
    """
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection non trouvée")

    steps = []
    for step_info in STEP_LABELS:
        step_num = step_info["step"]
        if step_num < inspection.progression:
            state = "completed"
        elif step_num == inspection.progression:
            state = "active"
        else:
            state = "locked"
        steps.append({**step_info, "state": state})

    return {
        "inspection_id": str(inspection_id),
        "progression": inspection.progression,
        "status": inspection.status,
        "percentage": inspection.progression * 25,
        "steps": steps,
    }


@router.post("/{inspection_id}/progress/next")
async def advance_progress(inspection_id: UUID, db: AsyncSession = Depends(get_db)):
    """Passe à l'étape suivante de progression.

    Args:
        inspection_id: UUID de l'inspection à faire avancer.
        db: Session async SQLAlchemy.

    Returns:
        Dictionnaire avec la nouvelle progression et le statut.

    Raises:
        HTTPException: 404 si l'inspection n'existe pas,
                       400 si elle est déjà terminée.
    """
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection non trouvée")
    if inspection.progression >= 4:
        raise HTTPException(status_code=400, detail="Inspection déjà terminée")

    inspection.progression += 1
    # Mettre à jour le statut correspondant
    status_map = {
        1: InspectionStatus.created,
        2: InspectionStatus.images_uploaded,
        3: InspectionStatus.processing,
        4: InspectionStatus.report_ready,
    }
    if inspection.progression in status_map:
        inspection.status = status_map[inspection.progression]
    await db.commit()
    return {"progression": inspection.progression, "status": inspection.status}
