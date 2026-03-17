"""Endpoints FastAPI pour la gestion des centrales solaires (wizard)."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.site import BosComponent, PanelModule, Site
from schemas.site import (
    BosComponentCreate,
    BosComponentResponse,
    KmlUploadResponse,
    PanelModuleCreate,
    PanelModuleResponse,
    SiteCreate,
    SiteResponse,
    SiteUpdate,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_site_or_404(site_id: uuid.UUID, db: AsyncSession) -> Site:
    """Récupère un site par son identifiant ou lève une 404."""
    result = await db.execute(
        select(Site)
        .options(selectinload(Site.panels), selectinload(Site.bos_components))
        .where(Site.id == site_id)
    )
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site {site_id} introuvable")
    return site


# ---------------------------------------------------------------------------
# CRUD sites
# ---------------------------------------------------------------------------

@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    payload: SiteCreate,
    db: AsyncSession = Depends(get_db),
) -> SiteResponse:
    """Crée une nouvelle centrale solaire."""
    site = Site(**payload.model_dump())
    db.add(site)
    await db.flush()
    await db.refresh(site)
    # Charger les relations vides pour la réponse
    await db.execute(
        select(Site)
        .options(selectinload(Site.panels), selectinload(Site.bos_components))
        .where(Site.id == site.id)
    )
    return SiteResponse.model_validate(site)


@router.get("/", response_model=list[SiteResponse])
async def list_sites(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(20, ge=1, le=100, description="Nombre max de résultats"),
    db: AsyncSession = Depends(get_db),
) -> list[SiteResponse]:
    """Retourne la liste paginée des centrales solaires."""
    result = await db.execute(
        select(Site)
        .options(selectinload(Site.panels), selectinload(Site.bos_components))
        .offset(skip)
        .limit(limit)
    )
    sites = result.scalars().all()
    return [SiteResponse.model_validate(s) for s in sites]


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SiteResponse:
    """Retourne les détails d'une centrale avec ses modules et composants BOS."""
    site = await _get_site_or_404(site_id, db)
    return SiteResponse.model_validate(site)


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: uuid.UUID,
    payload: SiteUpdate,
    db: AsyncSession = Depends(get_db),
) -> SiteResponse:
    """Met à jour les informations d'une centrale solaire."""
    site = await _get_site_or_404(site_id, db)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(site, field, value)
    await db.flush()
    await db.refresh(site)
    return SiteResponse.model_validate(site)


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Supprime une centrale et toutes ses données associées."""
    site = await _get_site_or_404(site_id, db)
    await db.delete(site)


# ---------------------------------------------------------------------------
# Modules panneaux
# ---------------------------------------------------------------------------

@router.post(
    "/{site_id}/panels",
    response_model=PanelModuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_panel_module(
    site_id: uuid.UUID,
    payload: PanelModuleCreate,
    db: AsyncSession = Depends(get_db),
) -> PanelModuleResponse:
    """Ajoute un module de panneau PV à une centrale."""
    # Vérifier que le site existe
    await _get_site_or_404(site_id, db)
    panel = PanelModule(site_id=site_id, **payload.model_dump())
    db.add(panel)
    await db.flush()
    await db.refresh(panel)
    return PanelModuleResponse.model_validate(panel)


@router.get("/{site_id}/panels", response_model=list[PanelModuleResponse])
async def list_panel_modules(
    site_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[PanelModuleResponse]:
    """Liste les modules de panneaux PV d'une centrale."""
    # Vérifier que le site existe
    await _get_site_or_404(site_id, db)
    result = await db.execute(
        select(PanelModule).where(PanelModule.site_id == site_id)
    )
    panels = result.scalars().all()
    return [PanelModuleResponse.model_validate(p) for p in panels]


# ---------------------------------------------------------------------------
# Composants BOS
# ---------------------------------------------------------------------------

@router.post(
    "/{site_id}/bos",
    response_model=BosComponentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_bos_component(
    site_id: uuid.UUID,
    payload: BosComponentCreate,
    db: AsyncSession = Depends(get_db),
) -> BosComponentResponse:
    """Ajoute un composant BOS à une centrale."""
    # Vérifier que le site existe
    await _get_site_or_404(site_id, db)
    component = BosComponent(site_id=site_id, **payload.model_dump())
    db.add(component)
    await db.flush()
    await db.refresh(component)
    return BosComponentResponse.model_validate(component)


@router.get("/{site_id}/bos", response_model=list[BosComponentResponse])
async def list_bos_components(
    site_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[BosComponentResponse]:
    """Liste les composants BOS d'une centrale."""
    # Vérifier que le site existe
    await _get_site_or_404(site_id, db)
    result = await db.execute(
        select(BosComponent).where(BosComponent.site_id == site_id)
    )
    components = result.scalars().all()
    return [BosComponentResponse.model_validate(c) for c in components]


# ---------------------------------------------------------------------------
# Upload KML / KMZ
# ---------------------------------------------------------------------------

@router.post("/{site_id}/kml", response_model=KmlUploadResponse)
async def upload_kml(
    site_id: uuid.UUID,
    file: UploadFile = File(..., description="Fichier KML ou KMZ du périmètre du site"),
    db: AsyncSession = Depends(get_db),
) -> KmlUploadResponse:
    """Importe un fichier KML/KMZ, calcule la surface et met à jour le site."""
    # Vérifier le type de fichier
    filename = file.filename or ""
    if not (filename.lower().endswith(".kml") or filename.lower().endswith(".kmz")):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Le fichier doit être au format .kml ou .kmz",
        )

    site = await _get_site_or_404(site_id, db)

    # Lire le contenu du fichier
    content: bytes = await file.read()

    # Appeler le parseur KML du module processing
    import json as json_module
    from processing.kml_parser import parse_kml_file, KmlParseResult

    try:
        result: KmlParseResult = parse_kml_file(content, filename)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    geojson_str: str = json_module.dumps(result.geojson)

    # Mettre à jour le site
    site.kml_file_name = filename
    site.kml_surface_ha = result.surface_ha
    site.kml_geojson = geojson_str
    if result.centroid_lat is not None and site.latitude is None:
        site.latitude = result.centroid_lat
    if result.centroid_lon is not None and site.longitude is None:
        site.longitude = result.centroid_lon

    await db.flush()

    return KmlUploadResponse(
        surface_ha=result.surface_ha,
        panel_count_estimate=result.panel_count_estimate,
        centroid_lat=result.centroid_lat,
        centroid_lon=result.centroid_lon,
        geojson=geojson_str,
    )
