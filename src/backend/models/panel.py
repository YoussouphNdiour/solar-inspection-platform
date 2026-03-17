"""Modèle SQLAlchemy pour les panneaux photovoltaïques individuels."""

import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Panel(Base):
    """Panneau photovoltaïque individuel d'un site solaire."""

    __tablename__ = "panels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    string_id: Mapped[str] = mapped_column(String(50), nullable=False)
    row_num: Mapped[int] = mapped_column(Integer, nullable=False)
    position_num: Mapped[int] = mapped_column(Integer, nullable=False)
    geometry: Mapped[object] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relations
    site: Mapped["Site"] = relationship("Site", back_populates="panels")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Panel id={self.id} string={self.string_id!r} row={self.row_num} pos={self.position_num}>"
