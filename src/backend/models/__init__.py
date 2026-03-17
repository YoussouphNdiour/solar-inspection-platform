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
from models.inspection import (
    Inspection,
    InspectionImage,
    InspectionStatus,
    ImageType,
    ImageProcessingStatus,
    PaymentStatus,
    PlanType,
    calculate_service_fee,
    PRICE_PER_PANEL,
    BANK_COMMISSION_PCT,
)
from models.image import Image
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
    # Drone
    "Drone",
    "DroneModel",
    # Inspection (nouveau modèle wizard)
    "Inspection",
    "InspectionImage",
    "InspectionStatus",
    "ImageType",
    "ImageProcessingStatus",
    "PaymentStatus",
    "PlanType",
    "calculate_service_fee",
    "PRICE_PER_PANEL",
    "BANK_COMMISSION_PCT",
    # Modèles hérités (compatibilité)
    "Image",
    "Panel",
]
