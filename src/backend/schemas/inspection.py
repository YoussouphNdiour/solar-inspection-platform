"""Schémas Pydantic v2 pour les examens d'inspection drone."""

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from models.inspection import ImageProcessingStatus, ImageType, InspectionStatus, PaymentStatus, PlanType


# ---------------------------------------------------------------------------
# Inspection — création / mise à jour / réponse
# ---------------------------------------------------------------------------


class InspectionCreate(BaseModel):
    """Données requises pour créer un examen d'inspection."""

    site_id: uuid.UUID = Field(..., description="Identifiant du site à inspecter")
    plan_type: PlanType = Field(
        PlanType.professional_5gsd, description="Type de plan (résolution GSD)"
    )
    drone_manufacturer: str | None = Field(None, description="Fabricant du drone")
    drone_model: str | None = Field(None, description="Modèle du drone")
    drone_serial_number: str | None = Field(None, description="Numéro de série du drone")
    flight_date: date | None = Field(None, description="Date de vol prévue")
    weather_conditions: dict[str, Any] | None = Field(
        None, description="Conditions météo (irradiance, vent, température, …)"
    )


class InspectionUpdate(BaseModel):
    """Mise à jour partielle d'un examen d'inspection — tous les champs optionnels."""

    plan_type: PlanType | None = None
    drone_manufacturer: str | None = None
    drone_model: str | None = None
    drone_serial_number: str | None = None
    flight_date: date | None = None
    weather_conditions: dict[str, Any] | None = None
    status: InspectionStatus | None = None
    progression: int | None = Field(None, ge=0, le=4)
    report_data: dict[str, Any] | None = None
    work_orders: dict[str, Any] | None = None


class InspectionResponse(BaseModel):
    """Réponse API complète pour un examen d'inspection."""

    id: uuid.UUID
    site_id: uuid.UUID
    org_id: uuid.UUID | None
    plan_type: PlanType
    gsd_target_cm: float
    drone_manufacturer: str | None
    drone_model: str | None
    drone_serial_number: str | None
    service_fee_usd: float | None
    bank_commission_pct: float
    total_amount_usd: float | None
    payment_status: PaymentStatus
    status: InspectionStatus
    progression: int
    flight_date: date | None
    weather_conditions: dict[str, Any] | None
    anomalies_geojson: str | None
    processing_status: str | None
    report_data: dict[str, Any] | None
    work_orders: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime | None
    # Champs calculés à partir des relations
    images_count: int = Field(0, description="Nombre d'images associées")
    site_name: str | None = Field(None, description="Nom du site inspecté")

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# InspectionImage
# ---------------------------------------------------------------------------


class InspectionImageResponse(BaseModel):
    """Réponse API pour une image d'inspection."""

    id: uuid.UUID
    inspection_id: uuid.UUID
    image_type: ImageType
    filename: str
    storage_url: str | None
    file_size_bytes: int | None
    gps_latitude: float | None
    gps_longitude: float | None
    gps_altitude_m: float | None
    capture_timestamp: datetime | None
    exif_data: dict[str, Any] | None
    processing_status: ImageProcessingStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Paiement
# ---------------------------------------------------------------------------


class PaymentUpdateRequest(BaseModel):
    """Requête de mise à jour du statut de paiement."""

    payment_status: PaymentStatus = Field(..., description="Nouveau statut de paiement")
    transaction_id: str | None = Field(None, description="Identifiant de transaction bancaire")


# ---------------------------------------------------------------------------
# Progression
# ---------------------------------------------------------------------------


class StepInfo(BaseModel):
    """Informations sur une étape de progression."""

    step: int
    label: str
    icon: str
    state: str = Field(..., description="completed | active | locked")


class ProgressResponse(BaseModel):
    """Réponse de progression d'un examen d'inspection."""

    inspection_id: str
    progression: int = Field(..., ge=0, le=4, description="Étape actuelle (0-4)")
    status: InspectionStatus
    percentage: int = Field(..., ge=0, le=100, description="Pourcentage d'avancement (0-100)")
    steps: list[StepInfo] = Field(..., description="Liste des 5 étapes avec leur état")


# ---------------------------------------------------------------------------
# Upload d'images
# ---------------------------------------------------------------------------


class ImageUploadResponse(BaseModel):
    """Réponse après upload de fichiers images."""

    uploaded_count: int = Field(..., description="Nombre total de fichiers acceptés")
    rgb_count: int = Field(..., description="Nombre d'images RGB uploadées")
    thermal_count: int = Field(..., description="Nombre d'images thermiques uploadées")
    errors: list[str] = Field(default_factory=list, description="Erreurs éventuelles par fichier")
