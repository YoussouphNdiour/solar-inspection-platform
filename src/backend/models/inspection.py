"""Modèle SQLAlchemy pour les inspections de sites solaires."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class InspectionStatus(str, Enum):
    """Statut d'une inspection."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Inspection(Base):
    """Session d'inspection drone d'un site solaire."""

    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    drone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drones.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=InspectionStatus.PLANNED
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Conditions météo IEC 62446-3
    irradiance_wm2: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_speed_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    ambient_temp_c: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Résultats pipeline — stockés en JSON (remplace shared/ filesystem sur Render)
    anomalies_geojson: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    processing_status: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    work_orders: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relations
    site: Mapped["Site"] = relationship("Site", back_populates="inspections")  # noqa: F821
    drone: Mapped["Drone | None"] = relationship("Drone", back_populates="inspections")  # noqa: F821
    images: Mapped[list["Image"]] = relationship(  # noqa: F821
        "Image", back_populates="inspection", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Inspection id={self.id} site={self.site_id} status={self.status!r}>"
