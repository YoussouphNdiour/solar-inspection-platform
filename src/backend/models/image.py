"""Modèle SQLAlchemy pour les images (RGB et thermiques)."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ImageType(str, Enum):
    """Type de capteur de l'image."""

    RGB = "rgb"
    THERMAL = "thermal"


class Image(Base):
    """Image capturée lors d'une inspection (RGB ou thermique)."""

    __tablename__ = "images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    image_type: Mapped[str] = mapped_column(String(10), nullable=False)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    gps_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relations — back_populates retiré : Inspection.images pointe désormais
    # vers InspectionImage, pas vers Image.
    inspection: Mapped["Inspection"] = relationship("Inspection", foreign_keys=[inspection_id])  # noqa: F821

    def __repr__(self) -> str:
        return f"<Image id={self.id} type={self.image_type!r} path={self.file_path!r}>"
