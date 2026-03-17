"""Schémas Pydantic pour la validation et la sérialisation."""

from schemas.site import SiteCreate, SiteRead, SiteUpdate
from schemas.drone import DroneCreate, DroneRead
from schemas.inspection import InspectionCreate, InspectionRead, InspectionStatusUpdate
from schemas.panel import PanelCreate, PanelRead

__all__ = [
    "SiteCreate", "SiteRead", "SiteUpdate",
    "DroneCreate", "DroneRead",
    "InspectionCreate", "InspectionRead", "InspectionStatusUpdate",
    "PanelCreate", "PanelRead",
]
