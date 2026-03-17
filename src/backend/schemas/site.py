"""Schémas Pydantic pour les centrales solaires (wizard de création)."""

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.site import AzimuthDirection, BosComponentType, MountingType, PanelType, PowerUnit, SiteStatus, SiteType


# ---------------------------------------------------------------------------
# PanelModule schemas
# ---------------------------------------------------------------------------

class PanelModuleCreate(BaseModel):
    """Données pour créer un module de panneau solaire."""

    brand: Optional[str] = Field(None, max_length=100, description="Marque du fabricant")
    model: Optional[str] = Field(None, max_length=100, description="Référence du modèle")
    panel_type: PanelType = Field(PanelType.mono, description="Technologie PV")
    cell_count: Optional[int] = Field(None, ge=1, description="Nombre de cellules par panneau")
    power_w: Optional[float] = Field(None, gt=0, description="Puissance crête par panneau (Wc)")
    panel_count: int = Field(1, ge=1, description="Nombre total de panneaux de ce modèle")
    warranty_start_date: Optional[date] = Field(None, description="Date de début de garantie")
    product_warranty_years: Optional[int] = Field(None, ge=0, description="Garantie produit (ans)")
    hardware_warranty_years: Optional[int] = Field(None, ge=0, description="Garantie matérielle (ans)")
    performance_warranty_years: Optional[int] = Field(None, ge=0, description="Garantie performance (ans)")


class PanelModuleResponse(PanelModuleCreate):
    """Réponse API pour un module de panneau."""

    id: uuid.UUID
    site_id: uuid.UUID

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# BosComponent schemas
# ---------------------------------------------------------------------------

class BosComponentCreate(BaseModel):
    """Données pour créer un composant BOS."""

    component_type: BosComponentType = Field(..., description="Type de composant BOS")
    brand: Optional[str] = Field(None, max_length=100, description="Marque")
    model: Optional[str] = Field(None, max_length=100, description="Modèle")
    quantity: int = Field(1, ge=1, description="Quantité installée")


class BosComponentResponse(BosComponentCreate):
    """Réponse API pour un composant BOS."""

    id: uuid.UUID
    site_id: uuid.UUID

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# KML upload schema
# ---------------------------------------------------------------------------

class KmlUploadResponse(BaseModel):
    """Résultat du traitement d'un fichier KML/KMZ."""

    surface_ha: Optional[float] = Field(None, description="Surface calculée en hectares")
    panel_count_estimate: Optional[int] = Field(None, description="Estimation du nombre de panneaux")
    centroid_lat: Optional[float] = Field(None, description="Latitude du centroïde")
    centroid_lon: Optional[float] = Field(None, description="Longitude du centroïde")
    geojson: Optional[str] = Field(None, description="Périmètre du site en GeoJSON (texte)")


# ---------------------------------------------------------------------------
# Site schemas
# ---------------------------------------------------------------------------

class SiteCreate(BaseModel):
    """Données pour créer une centrale solaire (wizard complet)."""

    name: str = Field(..., min_length=1, max_length=255, description="Nom de la centrale")
    org_id: Optional[uuid.UUID] = Field(None, description="Identifiant de l'organisation")
    site_type: SiteType = Field(SiteType.ground, description="Type de centrale")
    installation_date: Optional[date] = Field(None, description="Date de mise en service")
    mounting_type: MountingType = Field(MountingType.fixed, description="Type de montage")
    tilt_angle_deg: Optional[float] = Field(30.0, ge=0, le=90, description="Angle d'inclinaison (°)")
    azimuth_direction: Optional[AzimuthDirection] = Field(AzimuthDirection.S, description="Orientation cardinale")
    azimuth_degrees: Optional[float] = Field(180.0, ge=0, lt=360, description="Azimut exact (°)")
    dc_power_installed_kw: Optional[float] = Field(None, gt=0, description="Puissance DC installée")
    dc_power_unit: PowerUnit = Field(PowerUnit.kW, description="Unité de puissance")
    energy_sale_price: Optional[float] = Field(None, ge=0, description="Prix de vente de l'énergie")
    currency: Optional[str] = Field("USD", max_length=10, description="Devise (ex. USD, EUR)")
    address_line1: Optional[str] = Field(None, max_length=255, description="Adresse ligne 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Adresse ligne 2")
    district: Optional[str] = Field(None, max_length=100, description="Quartier / district")
    city: Optional[str] = Field(None, max_length=100, description="Ville")
    state_province: Optional[str] = Field(None, max_length=100, description="État / province")
    country: Optional[str] = Field(None, max_length=100, description="Pays")
    postal_code: Optional[str] = Field(None, max_length=20, description="Code postal")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude GPS")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude GPS")
    status: SiteStatus = Field(SiteStatus.active, description="Statut opérationnel")


class SiteUpdate(BaseModel):
    """Données pour modifier une centrale solaire (tous les champs optionnels)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    org_id: Optional[uuid.UUID] = None
    site_type: Optional[SiteType] = None
    installation_date: Optional[date] = None
    mounting_type: Optional[MountingType] = None
    tilt_angle_deg: Optional[float] = Field(None, ge=0, le=90)
    azimuth_direction: Optional[AzimuthDirection] = None
    azimuth_degrees: Optional[float] = Field(None, ge=0, lt=360)
    dc_power_installed_kw: Optional[float] = Field(None, gt=0)
    dc_power_unit: Optional[PowerUnit] = None
    energy_sale_price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    district: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    status: Optional[SiteStatus] = None


class SiteResponse(BaseModel):
    """Réponse API complète pour une centrale solaire."""

    id: uuid.UUID
    org_id: Optional[uuid.UUID]
    name: str
    site_type: SiteType
    installation_date: Optional[date]
    mounting_type: MountingType
    tilt_angle_deg: Optional[float]
    azimuth_direction: Optional[AzimuthDirection]
    azimuth_degrees: Optional[float]
    dc_power_installed_kw: Optional[float]
    dc_power_unit: PowerUnit
    energy_sale_price: Optional[float]
    currency: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    district: Optional[str]
    city: Optional[str]
    state_province: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    kml_file_url: Optional[str]
    kml_file_name: Optional[str]
    kml_surface_ha: Optional[float]
    kml_geojson: Optional[str]
    status: SiteStatus
    created_at: datetime
    updated_at: Optional[datetime]
    panels: list[PanelModuleResponse] = Field(default_factory=list)
    bos_components: list[BosComponentResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# Alias rétro-compatible (utilisé par les anciens endpoints)
SiteRead = SiteResponse
