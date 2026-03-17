"""Ajout tables panel_modules et bos_components + colonnes wizard sur sites.

Revision ID: 002
Revises: 001
Create Date: 2026-03-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Nouvelles colonnes sur la table sites
    # ------------------------------------------------------------------
    # Chaque add_column est enveloppé pour tolérer les colonnes déjà existantes.
    new_site_columns = [
        ("org_id", sa.Column("org_id", UUID(as_uuid=True), nullable=True)),
        ("site_type", sa.Column("site_type", sa.String(30), nullable=True, server_default="ground")),
        ("installation_date", sa.Column("installation_date", sa.Date(), nullable=True)),
        ("mounting_type", sa.Column("mounting_type", sa.String(30), nullable=True, server_default="fixed")),
        ("tilt_angle_deg", sa.Column("tilt_angle_deg", sa.Float(), nullable=True, server_default="30.0")),
        ("azimuth_direction", sa.Column("azimuth_direction", sa.String(5), nullable=True, server_default="S")),
        ("azimuth_degrees", sa.Column("azimuth_degrees", sa.Float(), nullable=True, server_default="180.0")),
        ("dc_power_installed_kw", sa.Column("dc_power_installed_kw", sa.Float(), nullable=True)),
        ("dc_power_unit", sa.Column("dc_power_unit", sa.String(5), nullable=True, server_default="kW")),
        ("energy_sale_price", sa.Column("energy_sale_price", sa.Float(), nullable=True)),
        ("currency", sa.Column("currency", sa.String(10), nullable=True, server_default="USD")),
        ("address_line1", sa.Column("address_line1", sa.String(255), nullable=True)),
        ("address_line2", sa.Column("address_line2", sa.String(255), nullable=True)),
        ("district", sa.Column("district", sa.String(100), nullable=True)),
        ("city", sa.Column("city", sa.String(100), nullable=True)),
        ("state_province", sa.Column("state_province", sa.String(100), nullable=True)),
        ("country", sa.Column("country", sa.String(100), nullable=True)),
        ("postal_code", sa.Column("postal_code", sa.String(20), nullable=True)),
        ("latitude", sa.Column("latitude", sa.Float(), nullable=True)),
        ("longitude", sa.Column("longitude", sa.Float(), nullable=True)),
        ("kml_file_url", sa.Column("kml_file_url", sa.String(500), nullable=True)),
        ("kml_file_name", sa.Column("kml_file_name", sa.String(255), nullable=True)),
        ("kml_surface_ha", sa.Column("kml_surface_ha", sa.Float(), nullable=True)),
        ("kml_geojson", sa.Column("kml_geojson", sa.Text(), nullable=True)),
        ("status", sa.Column("status", sa.String(20), nullable=True, server_default="active")),
    ]

    for col_name, col_def in new_site_columns:
        try:
            op.add_column("sites", col_def)
        except Exception:
            # Colonne déjà présente — ignorer
            pass

    # ------------------------------------------------------------------
    # Nouvelle table panel_modules
    # ------------------------------------------------------------------
    op.create_table(
        "panel_modules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "site_id",
            UUID(as_uuid=True),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("panel_type", sa.String(20), nullable=False, server_default="mono"),
        sa.Column("cell_count", sa.Integer(), nullable=True),
        sa.Column("power_w", sa.Float(), nullable=True),
        sa.Column("panel_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("warranty_start_date", sa.Date(), nullable=True),
        sa.Column("product_warranty_years", sa.Integer(), nullable=True),
        sa.Column("hardware_warranty_years", sa.Integer(), nullable=True),
        sa.Column("performance_warranty_years", sa.Integer(), nullable=True),
    )
    op.create_index("ix_panel_modules_site_id", "panel_modules", ["site_id"])

    # ------------------------------------------------------------------
    # Nouvelle table bos_components
    # ------------------------------------------------------------------
    op.create_table(
        "bos_components",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "site_id",
            UUID(as_uuid=True),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("component_type", sa.String(30), nullable=False),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_bos_components_site_id", "bos_components", ["site_id"])


def downgrade() -> None:
    op.drop_index("ix_bos_components_site_id", table_name="bos_components")
    op.drop_table("bos_components")

    op.drop_index("ix_panel_modules_site_id", table_name="panel_modules")
    op.drop_table("panel_modules")

    # Supprimer les nouvelles colonnes des sites
    columns_to_drop = [
        "org_id", "site_type", "installation_date", "mounting_type",
        "tilt_angle_deg", "azimuth_direction", "azimuth_degrees",
        "dc_power_installed_kw", "dc_power_unit", "energy_sale_price",
        "currency", "address_line1", "address_line2", "district", "city",
        "state_province", "country", "postal_code", "latitude", "longitude",
        "kml_file_url", "kml_file_name", "kml_surface_ha", "kml_geojson",
        "status",
    ]
    for col_name in columns_to_drop:
        try:
            op.drop_column("sites", col_name)
        except Exception:
            pass
