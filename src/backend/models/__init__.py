"""Modèles SQLAlchemy de la plateforme d'inspection solaire."""

from models.site import (
    AzimuthDirection,
    BosComponent,
    BosComponentType,
    MountingType,
    PanelModule,
    PanelType,
    PowerUnit,
    Site,
    SiteStatus,
    SiteType,
)
from models.drone import Drone, DroneModel
from models.inspection import Inspection, InspectionStatus
from models.image import Image, ImageType
from models.panel import Panel

__all__ = [
    # Site et sous-modèles
    "Site",
    "SiteType",
    "SiteStatus",
    "MountingType",
    "AzimuthDirection",
    "PowerUnit",
    "PanelModule",
    "PanelType",
    "BosComponent",
    "BosComponentType",
    # Autres modèles
    "Drone",
    "DroneModel",
    "Inspection",
    "InspectionStatus",
    "Image",
    "ImageType",
    "Panel",
]
