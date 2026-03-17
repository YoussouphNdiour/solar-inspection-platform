"""Endpoints FastAPI pour la gestion des sites de centrale solaire."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.site import Site
from schemas.site import SiteCreate, SiteRead, SiteUpdate

router = APIRouter()


@router.get("/", response_model=list[SiteRead])
async def list_sites(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(20, ge=1, le=100, description="Nombre max de résultats"),
    db: AsyncSession = Depends(get_db),
) -> list[SiteRead]:
    """Retourne la liste paginée des sites solaires."""
    result = await db.execute(select(Site).offset(skip).limit(limit))
    sites = result.scalars().all()
    return [SiteRead.model_validate(s) for s in sites]


@router.post("/", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
async def create_site(
    payload: SiteCreate,
    db: AsyncSession = Depends(get_db),
) -> SiteRead:
    """Crée un nouveau site solaire."""
    from geoalchemy2.shape import from_shape
    from shapely.geometry import shape

    geom = shape(payload.location)
    site = Site(
        name=payload.name,
        location=from_shape(geom, srid=4326),
        surface_m2=payload.surface_m2,
        panel_count=payload.panel_count,
    )
    db.add(site)
    await db.flush()
    await db.refresh(site)
    return SiteRead.model_validate(site)


@router.get("/{site_id}", response_model=SiteRead)
async def get_site(
    site_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SiteRead:
    """Retourne les détails d'un site."""
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site {site_id} introuvable")
    return SiteRead.model_validate(site)


@router.put("/{site_id}", response_model=SiteRead)
async def update_site(
    site_id: uuid.UUID,
    payload: SiteUpdate,
    db: AsyncSession = Depends(get_db),
) -> SiteRead:
    """Met à jour les informations d'un site."""
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site {site_id} introuvable")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(site, field, value)

    await db.flush()
    await db.refresh(site)
    return SiteRead.model_validate(site)


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Supprime un site et toutes ses données associées."""
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site {site_id} introuvable")
    await db.delete(site)
