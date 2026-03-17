"""Modèle SQLAlchemy pour les centrales solaires."""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class SiteType(str, enum.Enum):
    """Type de centrale solaire."""

    ground = "ground"
    rooftop = "rooftop"
    residential = "residential"
    floating = "floating"


class MountingType(str, enum.Enum):
    """Type de montage des panneaux."""

    fixed = "fixed"
    tracker_single_axis = "tracker_single_axis"
    tracker_dual_axis = "tracker_dual_axis"


class AzimuthDirection(str, enum.Enum):
    """Direction azimutale d'orientation des panneaux."""

    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


class PowerUnit(str, enum.Enum):
    """Unité de puissance installée."""

    kW = "kW"
    MW = "MW"


class SiteStatus(str, enum.Enum):
    """Statut opérationnel d'une centrale."""

    active = "active"
    inactive = "inactive"


class PanelType(str, enum.Enum):
    """Technologie du module photovoltaïque."""

    mono = "mono"
    poly = "poly"
    bifacial = "bifacial"
    thin_film = "thin_film"


class BosComponentType(str, enum.Enum):
    """Type de composant BOS (Balance of System)."""

    inverter = "inverter"
    combiner_box = "combiner_box"
    cable = "cable"
    mounting = "mounting"
    monitoring = "monitoring"


class Site(Base):
    """Centrale solaire à inspecter."""

    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String(255), nullable=False)
    site_type = Column(Enum(SiteType), nullable=False, default=SiteType.ground)
    installation_date = Column(Date, nullable=True)
    mounting_type = Column(Enum(MountingType), nullable=False, default=MountingType.fixed)
    tilt_angle_deg = Column(Float, nullable=True, default=30.0)
    azimuth_direction = Column(Enum(AzimuthDirection), nullable=True, default=AzimuthDirection.S)
    azimuth_degrees = Column(Float, nullable=True, default=180.0)
    dc_power_installed_kw = Column(Float, nullable=True)
    dc_power_unit = Column(Enum(PowerUnit), nullable=False, default=PowerUnit.kW)
    energy_sale_price = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True, default="USD")
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    district = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    kml_file_url = Column(String(500), nullable=True)
    kml_file_name = Column(String(255), nullable=True)
    kml_surface_ha = Column(Float, nullable=True)
    kml_geojson = Column(String, nullable=True)  # GeoJSON text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(Enum(SiteStatus), nullable=False, default=SiteStatus.active)

    # Relations
    inspections = relationship(
        "Inspection", back_populates="site", cascade="all, delete-orphan"
    )
    panels = relationship(
        "PanelModule", back_populates="site", cascade="all, delete-orphan"
    )
    bos_components = relationship(
        "BosComponent", back_populates="site", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Site id={self.id} name={self.name!r}>"


class PanelModule(Base):
    """Module photovoltaïque installé sur un site."""

    __tablename__ = "panel_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    panel_type = Column(Enum(PanelType), nullable=False, default=PanelType.mono)
    cell_count = Column(Integer, nullable=True)
    power_w = Column(Float, nullable=True)
    panel_count = Column(Integer, nullable=False, default=1)
    warranty_start_date = Column(Date, nullable=True)
    product_warranty_years = Column(Integer, nullable=True)
    hardware_warranty_years = Column(Integer, nullable=True)
    performance_warranty_years = Column(Integer, nullable=True)

    # Relations
    site = relationship("Site", back_populates="panels")

    def __repr__(self) -> str:
        return f"<PanelModule id={self.id} brand={self.brand!r} model={self.model!r}>"


class BosComponent(Base):
    """Composant BOS (Balance of System) d'un site solaire."""

    __tablename__ = "bos_components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    component_type = Column(Enum(BosComponentType), nullable=False)
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)

    # Relations
    site = relationship("Site", back_populates="bos_components")

    def __repr__(self) -> str:
        return f"<BosComponent id={self.id} type={self.component_type!r}>"
