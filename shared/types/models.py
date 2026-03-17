"""Modèles Pydantic partagés entre agents — types canoniques de la plateforme."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CoAClass(str, Enum):
    """Classification IEC 62446-3 des anomalies thermiques."""

    COA1 = "CoA1"
    COA2 = "CoA2"
    COA3 = "CoA3"


class AnomalyType(str, Enum):
    """Types d'anomalies détectées sur les panneaux solaires."""

    HOTSPOT_CELLULE = "hotspot_cellule"
    BYPASS_DIODE = "bypass_diode"
    PID = "pid"
    STRING_OUVERTE = "string_ouverte"
    OMBRAGE = "ombrage"
    SALISSURE = "salissure"
    SAIN = "sain"


class SiteBase(BaseModel):
    """Centrale solaire."""

    id: uuid.UUID
    name: str
    location: dict[str, Any]  # GeoJSON Point
    surface_m2: float
    panel_count: int
    created_at: datetime


class InspectionBase(BaseModel):
    """Session d'inspection drone."""

    id: uuid.UUID
    site_id: uuid.UUID
    drone_id: uuid.UUID | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    irradiance_wm2: float | None
    wind_speed_ms: float | None
    ambient_temp_c: float | None


class AnomalyBase(BaseModel):
    """Anomalie détectée sur un panneau."""

    panel_id: str
    delta_t_measured: float
    delta_t_normalized: float
    coa_class: CoAClass
    anomaly_type: AnomalyType
    confidence: float = Field(..., ge=0.0, le=1.0)
    geometry: dict[str, Any]  # GeoJSON Polygon


class FlightPlanBase(BaseModel):
    """Plan de vol drone."""

    site_id: str
    drone_model: str
    altitude_m: float
    speed_ms: float
    frontal_overlap_pct: float
    lateral_overlap_pct: float
    gsd_rgb_cm: float
    gsd_thermal_cm: float
    estimated_duration_min: float
    battery_cycles: int
