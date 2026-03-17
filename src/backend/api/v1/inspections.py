"""Endpoints FastAPI pour la gestion des examens d'inspection drone."""

import asyncio
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import settings
from database import get_db
from models.inspection import (
    ImageProcessingStatus,
    ImageType,
    Inspection,
    InspectionImage,
    InspectionStatus,
    PaymentStatus,
    PlanType,
    calculate_service_fee,
)
from models.site import PanelModule, Site
from schemas.inspection import (
    ImageUploadResponse,
    InspectionCreate,
    InspectionImageResponse,
    InspectionResponse,
    InspectionUpdate,
    PaymentUpdateRequest,
    ProgressResponse,
    StepInfo,
)

router = APIRouter()

# Répertoire de stockage local des images brutes
_RAW_IMAGES_BASE = Path(__file__).resolve().parents[5] / "shared" / "raw_images"

# Étapes de progression
STEP_LABELS = [
    {"step": 0, "label": "Paiement", "icon": "💳"},
    {"step": 1, "label": "Téléchargement", "icon": "⬆️"},
    {"step": 2, "label": "Évaluation", "icon": "👁️"},
    {"step": 3, "label": "Analyse", "icon": "📊"},
    {"step": 4, "label": "Rapport", "icon": "📄"},
]


def _build_inspection_response(inspection: Inspection) -> InspectionResponse:
    """Construit un InspectionResponse à partir d'un objet ORM Inspection.

    Args:
        inspection: Instance ORM chargée depuis la base de données.

    Returns:
        Objet InspectionResponse sérialisable.
    """
    images_count = len(inspection.images) if inspection.images is not None else 0
    site_name = inspection.site.name if inspection.site else None
    data = {
        **{c.key: getattr(inspection, c.key) for c in inspection.__table__.columns},
        "images_count": images_count,
        "site_name": site_name,
    }
    return InspectionResponse.model_validate(data)


def _build_progress_response(inspection: Inspection) -> ProgressResponse:
    """Construit un ProgressResponse pour une inspection donnée.

    Args:
        inspection: Instance ORM.

    Returns:
        Objet ProgressResponse avec les 5 étapes.
    """
    steps: list[StepInfo] = []
    for step_info in STEP_LABELS:
        step_num = step_info["step"]
        if step_num < inspection.progression:
            state = "completed"
        elif step_num == inspection.progression:
            state = "active"
        else:
            state = "locked"
        steps.append(StepInfo(**step_info, state=state))

    return ProgressResponse(
        inspection_id=str(inspection.id),
        progression=inspection.progression,
        status=inspection.status,
        percentage=inspection.progression * 25,
        steps=steps,
    )


async def _get_inspection_or_404(
    inspection_id: uuid.UUID,
    db: AsyncSession,
    *,
    load_images: bool = False,
    load_site: bool = True,
) -> Inspection:
    """Récupère une inspection par son ID ou lève HTTP 404.

    Args:
        inspection_id: UUID de l'inspection.
        db: Session async SQLAlchemy.
        load_images: Si True, charge eagerly la relation images.
        load_site: Si True, charge eagerly la relation site.

    Returns:
        Instance Inspection.

    Raises:
        HTTPException: 404 si l'inspection n'existe pas.
    """
    query = select(Inspection).where(Inspection.id == inspection_id)
    if load_images:
        query = query.options(selectinload(Inspection.images))
    if load_site:
        query = query.options(selectinload(Inspection.site))
    result = await db.execute(query)
    inspection = result.scalar_one_or_none()
    if inspection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection {inspection_id} introuvable",
        )
    return inspection


# ---------------------------------------------------------------------------
# POST /api/v1/inspections
# ---------------------------------------------------------------------------


@router.post("/", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    payload: InspectionCreate,
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Crée un nouvel examen d'inspection et calcule les frais de service.

    Le nombre de panneaux est extrait du premier PanelModule du site.
    La GSD cible est déterminée par le type de plan choisi.
    """
    # Vérifier que le site existe
    site_result = await db.execute(
        select(Site)
        .where(Site.id == payload.site_id)
        .options(selectinload(Site.panels))
    )
    site = site_result.scalar_one_or_none()
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site {payload.site_id} introuvable",
        )

    # Calculer le nombre total de panneaux depuis panel_modules
    panel_count = sum(pm.panel_count for pm in site.panels) if site.panels else 0
    if panel_count == 0:
        # Fallback minimal pour permettre la création sans panels définis
        panel_count = 1

    # Frais de service
    service_fee, bank_commission, total = calculate_service_fee(payload.plan_type, panel_count)

    # GSD cible selon le plan
    gsd_target_cm = 3.0 if payload.plan_type == PlanType.enterprise_3gsd else 5.0

    inspection = Inspection(
        site_id=payload.site_id,
        plan_type=payload.plan_type,
        gsd_target_cm=gsd_target_cm,
        drone_manufacturer=payload.drone_manufacturer,
        drone_model=payload.drone_model,
        drone_serial_number=payload.drone_serial_number,
        flight_date=payload.flight_date,
        weather_conditions=payload.weather_conditions,
        service_fee_usd=service_fee,
        bank_commission_pct=5.0,
        total_amount_usd=total,
        payment_status=PaymentStatus.pending,
        status=InspectionStatus.created,
        progression=0,
    )
    db.add(inspection)
    await db.flush()
    await db.refresh(inspection)

    # Charger la relation site pour la réponse
    await db.refresh(inspection, attribute_names=["images", "site"])
    return _build_inspection_response(inspection)


# ---------------------------------------------------------------------------
# GET /api/v1/inspections
# ---------------------------------------------------------------------------


@router.get("/", response_model=list[InspectionResponse])
async def list_inspections(
    site_id: uuid.UUID | None = Query(None, description="Filtrer par site"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[InspectionResponse]:
    """Retourne la liste paginée des examens d'inspection."""
    query = (
        select(Inspection)
        .options(selectinload(Inspection.images), selectinload(Inspection.site))
        .offset(skip)
        .limit(limit)
    )
    if site_id:
        query = query.where(Inspection.site_id == site_id)

    result = await db.execute(query)
    inspections = result.scalars().all()
    return [_build_inspection_response(i) for i in inspections]


# ---------------------------------------------------------------------------
# GET /api/v1/inspections/{id}
# ---------------------------------------------------------------------------


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Retourne les détails d'un examen d'inspection avec le compte d'images."""
    inspection = await _get_inspection_or_404(
        inspection_id, db, load_images=True, load_site=True
    )
    return _build_inspection_response(inspection)


# ---------------------------------------------------------------------------
# PUT /api/v1/inspections/{id}/payment
# ---------------------------------------------------------------------------


@router.put("/{inspection_id}/payment", response_model=InspectionResponse)
async def update_payment(
    inspection_id: uuid.UUID,
    payload: PaymentUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Met à jour le statut de paiement d'un examen.

    Si le paiement est confirmé (paid), la progression passe à 1
    pour débloquer l'étape de téléchargement des images.
    """
    inspection = await _get_inspection_or_404(
        inspection_id, db, load_images=True, load_site=True
    )

    inspection.payment_status = payload.payment_status
    if payload.payment_status == PaymentStatus.paid and inspection.progression == 0:
        inspection.progression = 1

    await db.flush()
    await db.refresh(inspection)
    await db.refresh(inspection, attribute_names=["images", "site"])
    return _build_inspection_response(inspection)


# ---------------------------------------------------------------------------
# POST /api/v1/inspections/{id}/images
# ---------------------------------------------------------------------------


@router.post("/{inspection_id}/images", response_model=ImageUploadResponse)
async def upload_images(
    inspection_id: uuid.UUID,
    files: list[UploadFile] = File(..., description="Fichiers images RGB ou thermiques"),
    db: AsyncSession = Depends(get_db),
) -> ImageUploadResponse:
    """Accepte des images drone (RGB / thermique) et les enregistre.

    La détection du type se fait sur le nom du fichier :
    - '_T.' ou '_THERMAL' (insensible à la casse) → thermal
    - Sinon → rgb

    Les fichiers sont sauvegardés localement dans
    ``shared/raw_images/{inspection_id}/rgb/`` ou ``thermal/``.
    """
    inspection = await _get_inspection_or_404(
        inspection_id, db, load_images=False, load_site=False
    )

    uploaded_count = 0
    rgb_count = 0
    thermal_count = 0
    errors: list[str] = []

    for upload_file in files:
        try:
            filename = upload_file.filename or f"image_{uuid.uuid4()}"
            upper_name = filename.upper()

            # Détecter le type d'image
            if "_T." in upper_name or "_THERMAL" in upper_name:
                img_type = ImageType.thermal
                sub_dir = "thermal"
            else:
                img_type = ImageType.rgb
                sub_dir = "rgb"

            # Lire le contenu du fichier
            content = await upload_file.read()
            file_size = len(content)

            # Sauvegarder localement
            dest_dir = _RAW_IMAGES_BASE / str(inspection_id) / sub_dir
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / filename
            dest_path.write_bytes(content)
            storage_url = str(dest_path)

            # Extraction EXIF (optionnelle)
            exif_data: dict | None = None
            gps_lat: float | None = None
            gps_lon: float | None = None
            gps_alt: float | None = None
            try:
                import io
                import exifread  # type: ignore[import]

                tags = exifread.process_file(io.BytesIO(content), details=False)
                exif_data = {k: str(v) for k, v in tags.items()}

                def _ratio_to_float(tag_value) -> float | None:
                    """Convertit une valeur IFDRatio en float."""
                    try:
                        ratios = tag_value.values
                        if len(ratios) == 3:
                            deg = float(ratios[0].num) / float(ratios[0].den)
                            min_ = float(ratios[1].num) / float(ratios[1].den)
                            sec = float(ratios[2].num) / float(ratios[2].den)
                            return deg + min_ / 60 + sec / 3600
                    except Exception:
                        pass
                    return None

                if "GPS GPSLatitude" in tags:
                    gps_lat = _ratio_to_float(tags["GPS GPSLatitude"])
                    if "GPS GPSLatitudeRef" in tags and str(tags["GPS GPSLatitudeRef"]) == "S":
                        gps_lat = -gps_lat if gps_lat is not None else None
                if "GPS GPSLongitude" in tags:
                    gps_lon = _ratio_to_float(tags["GPS GPSLongitude"])
                    if "GPS GPSLongitudeRef" in tags and str(tags["GPS GPSLongitudeRef"]) == "W":
                        gps_lon = -gps_lon if gps_lon is not None else None
                if "GPS GPSAltitude" in tags:
                    try:
                        alt_ratio = tags["GPS GPSAltitude"].values[0]
                        gps_alt = float(alt_ratio.num) / float(alt_ratio.den)
                    except Exception:
                        pass
            except ImportError:
                # exifread non disponible — continuer sans EXIF
                pass
            except Exception:
                # Erreur EXIF non bloquante
                pass

            # Créer l'enregistrement en base
            img_record = InspectionImage(
                inspection_id=inspection_id,
                image_type=img_type,
                filename=filename,
                storage_url=storage_url,
                file_size_bytes=file_size,
                gps_latitude=gps_lat,
                gps_longitude=gps_lon,
                gps_altitude_m=gps_alt,
                exif_data=exif_data,
                processing_status=ImageProcessingStatus.uploaded,
            )
            db.add(img_record)

            uploaded_count += 1
            if img_type == ImageType.rgb:
                rgb_count += 1
            else:
                thermal_count += 1

        except Exception as exc:
            errors.append(f"{upload_file.filename}: {exc}")

    # Mettre à jour le statut de l'inspection
    if uploaded_count > 0:
        inspection.status = InspectionStatus.images_uploaded
        inspection.progression = max(inspection.progression, 2)

    await db.flush()

    return ImageUploadResponse(
        uploaded_count=uploaded_count,
        rgb_count=rgb_count,
        thermal_count=thermal_count,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/inspections/{id}/images
# ---------------------------------------------------------------------------


@router.get("/{inspection_id}/images", response_model=list[InspectionImageResponse])
async def list_images(
    inspection_id: uuid.UUID,
    image_type: ImageType | None = Query(None, description="Filtrer par type (rgb/thermal)"),
    db: AsyncSession = Depends(get_db),
) -> list[InspectionImageResponse]:
    """Retourne les images associées à un examen d'inspection."""
    # Vérifier que l'inspection existe
    await _get_inspection_or_404(inspection_id, db, load_images=False, load_site=False)

    query = select(InspectionImage).where(InspectionImage.inspection_id == inspection_id)
    if image_type is not None:
        query = query.where(InspectionImage.image_type == image_type)

    result = await db.execute(query)
    images = result.scalars().all()
    return [InspectionImageResponse.model_validate(img) for img in images]


# ---------------------------------------------------------------------------
# POST /api/v1/inspections/{id}/start-analysis
# ---------------------------------------------------------------------------


@router.post("/{inspection_id}/start-analysis")
async def start_analysis(
    inspection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Lance le pipeline d'analyse de l'inspection.

    Vérifie qu'au moins une image a été uploadée avant de démarrer.
    """
    inspection = await _get_inspection_or_404(
        inspection_id, db, load_images=True, load_site=False
    )

    if not inspection.images:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Aucune image uploadée. Veuillez d'abord télécharger des images.",
        )

    inspection.status = InspectionStatus.processing
    inspection.progression = max(inspection.progression, 3)
    await db.flush()

    return {"message": "Analyse lancée", "inspection_id": str(inspection_id)}


# ---------------------------------------------------------------------------
# GET /api/v1/inspections/{id}/status  (Server-Sent Events)
# ---------------------------------------------------------------------------


@router.get("/{inspection_id}/status")
async def stream_status(
    inspection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Retourne le statut en temps réel via Server-Sent Events (SSE).

    Envoie un événement toutes les 2 secondes avec progression, statut et
    pourcentage. Le stream s'arrête automatiquement après 60 secondes.
    """
    try:
        from sse_starlette.sse import EventSourceResponse  # type: ignore[import]

        async def event_generator():
            """Générateur d'événements SSE pour la progression."""
            for _ in range(30):  # max 30 itérations × 2 s = 60 s
                result = await db.execute(
                    select(Inspection).where(Inspection.id == inspection_id)
                )
                inspection = result.scalar_one_or_none()
                if inspection is None:
                    yield {
                        "data": json.dumps({"error": "Inspection introuvable"}),
                    }
                    return

                payload = {
                    "progression": inspection.progression,
                    "status": inspection.status,
                    "percentage": inspection.progression * 25,
                }
                yield {"data": json.dumps(payload)}

                if inspection.progression >= 4:
                    return

                await asyncio.sleep(2)

        return EventSourceResponse(event_generator())

    except ImportError:
        # Fallback si sse-starlette n'est pas installé
        async def simple_stream():
            result = await db.execute(
                select(Inspection).where(Inspection.id == inspection_id)
            )
            inspection = result.scalar_one_or_none()
            if inspection is None:
                yield b"data: {\"error\": \"Inspection introuvable\"}\n\n"
                return
            payload = {
                "progression": inspection.progression,
                "status": inspection.status,
                "percentage": inspection.progression * 25,
            }
            yield f"data: {json.dumps(payload)}\n\n".encode()

        return StreamingResponse(simple_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# GET /api/v1/inspections/{id}/progress
# ---------------------------------------------------------------------------


@router.get("/{inspection_id}/progress", response_model=ProgressResponse)
async def get_progress(
    inspection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    """Retourne la progression détaillée de l'examen avec les 5 étapes."""
    inspection = await _get_inspection_or_404(
        inspection_id, db, load_images=False, load_site=False
    )
    return _build_progress_response(inspection)


# ---------------------------------------------------------------------------
# Conserver les anciens endpoints pour compatibilité ascendante
# ---------------------------------------------------------------------------


@router.get("/{inspection_id}/anomalies")
async def get_inspection_anomalies(
    inspection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Retourne le GeoJSON des anomalies détectées pour une inspection.

    Priorité : colonne DB (Render) → fichier shared/ (local dev).
    """
    inspection = await _get_inspection_or_404(
        inspection_id, db, load_images=False, load_site=False
    )

    if inspection.anomalies_geojson:
        try:
            return json.loads(inspection.anomalies_geojson)
        except json.JSONDecodeError:
            return {"raw": inspection.anomalies_geojson}

    geojson_path = (
        Path(__file__).resolve().parents[5]
        / "shared"
        / "anomalies"
        / str(inspection_id)
        / "anomalies.geojson"
    )
    if geojson_path.exists():
        with open(geojson_path) as f:
            return json.load(f)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=(
            f"Aucune anomalie trouvée pour l'inspection {inspection_id}. "
            "Le pipeline de détection n'a pas encore été exécuté."
        ),
    )


@router.put("/{inspection_id}/anomalies")
async def upload_inspection_anomalies(
    inspection_id: uuid.UUID,
    geojson: dict,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Stocke le GeoJSON des anomalies en base de données (Render-compatible)."""
    inspection = await _get_inspection_or_404(
        inspection_id, db, load_images=False, load_site=False
    )
    inspection.anomalies_geojson = json.dumps(geojson)
    await db.flush()
    return {"status": "stored", "inspection_id": str(inspection_id)}
