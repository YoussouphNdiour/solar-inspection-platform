"""Modèle SQLAlchemy pour les examens d'inspection drone."""
import enum
import uuid
from datetime import date, datetime
from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class PlanType(str, enum.Enum):
    """Type de plan d'inspection."""

    professional_5gsd = "professional_5gsd"
    enterprise_3gsd = "enterprise_3gsd"


class PaymentStatus(str, enum.Enum):
    """Statut du paiement de l'inspection."""

    pending = "pending"
    paid = "paid"
    failed = "failed"


class InspectionStatus(str, enum.Enum):
    """Statut d'avancement de l'inspection."""

    created = "created"
    images_uploaded = "images_uploaded"
    processing = "processing"
    analysis_done = "analysis_done"
    report_ready = "report_ready"


class ImageType(str, enum.Enum):
    """Type d'image capturée par le drone."""

    rgb = "rgb"
    thermal = "thermal"


class ImageProcessingStatus(str, enum.Enum):
    """Statut de traitement d'une image."""

    uploaded = "uploaded"
    queued = "queued"
    processed = "processed"
    error = "error"


# Tarification par type de plan
PRICE_PER_PANEL = {
    PlanType.professional_5gsd: 0.094,
    PlanType.enterprise_3gsd: 0.150,
}
BANK_COMMISSION_PCT = 5.0


def calculate_service_fee(plan_type: PlanType, panel_count: int) -> tuple[float, float, float]:
    """Calcule frais de service, commission bancaire et total.

    Args:
        plan_type: Type de plan d'inspection choisi.
        panel_count: Nombre de panneaux à inspecter.

    Returns:
        Tuple (service_fee, bank_commission, total) en USD.
    """
    price = PRICE_PER_PANEL[plan_type]
    service_fee = round(panel_count * price, 2)
    bank_commission = round(service_fee * BANK_COMMISSION_PCT / 100, 2)
    total = round(service_fee + bank_commission, 2)
    return service_fee, bank_commission, total


class Inspection(Base):
    """Examen d'inspection drone d'un site solaire."""

    __tablename__ = "inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(UUID(as_uuid=True), nullable=True)
    plan_type = Column(Enum(PlanType), nullable=False, default=PlanType.professional_5gsd)
    gsd_target_cm = Column(Float, nullable=False, default=5.0)
    drone_manufacturer = Column(String(100), nullable=True)
    drone_model = Column(String(100), nullable=True)
    drone_serial_number = Column(String(100), nullable=True)
    service_fee_usd = Column(Float, nullable=True)
    bank_commission_pct = Column(Float, nullable=False, default=BANK_COMMISSION_PCT)
    total_amount_usd = Column(Float, nullable=True)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    status = Column(Enum(InspectionStatus), nullable=False, default=InspectionStatus.created)
    progression = Column(Integer, nullable=False, default=0)  # 0-4
    flight_date = Column(Date, nullable=True)
    weather_conditions = Column(JSON, nullable=True)
    anomalies_geojson = Column(String, nullable=True)
    processing_status = Column(String(50), nullable=True)
    report_data = Column(JSON, nullable=True)
    work_orders = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    site = relationship("Site", back_populates="inspections")
    images = relationship(
        "InspectionImage", back_populates="inspection", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Inspection id={self.id} site={self.site_id} status={self.status!r}>"


class InspectionImage(Base):
    """Image drone associée à un examen d'inspection."""

    __tablename__ = "inspection_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(
        UUID(as_uuid=True), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False
    )
    image_type = Column(Enum(ImageType), nullable=False, default=ImageType.rgb)
    filename = Column(String(255), nullable=False)
    storage_url = Column(String(1000), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    gps_altitude_m = Column(Float, nullable=True)
    capture_timestamp = Column(DateTime(timezone=True), nullable=True)
    exif_data = Column(JSON, nullable=True)
    processing_status = Column(
        Enum(ImageProcessingStatus), nullable=False, default=ImageProcessingStatus.uploaded
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    inspection = relationship("Inspection", back_populates="images")

    def __repr__(self) -> str:
        return f"<InspectionImage id={self.id} type={self.image_type!r} file={self.filename!r}>"
