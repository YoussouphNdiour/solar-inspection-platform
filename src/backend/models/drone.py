"""Modèle SQLAlchemy pour les drones d'inspection."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class DroneModel(str, Enum):
    """Modèles de drones supportés."""

    MAVIC_3T = "DJI Mavic 3T"
    MATRICE_30T = "Matrice 30T"
    MATRICE_300_RTK = "Matrice 300 RTK"


class DroneStatus(str, Enum):
    """Statut opérationnel du drone."""

    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class Drone(Base):
    """Drone utilisé pour les inspections."""

    __tablename__ = "drones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=DroneStatus.AVAILABLE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # La relation vers Inspection a été retirée car le nouveau modèle
    # Inspection ne contient plus de colonne drone_id.

    def __repr__(self) -> str:
        return f"<Drone id={self.id} model={self.model!r} sn={self.serial_number!r}>"
