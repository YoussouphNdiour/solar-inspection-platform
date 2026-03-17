"""Schéma initial — PostGIS + tables de base.

Revision ID: 001
Revises: —
Create Date: 2025-09-30
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostGIS — ignoré si non disponible (Render free tier)
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    except Exception:
        pass

    # Table sites
    op.create_table(
        "sites",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),  # WKT ou GeoJSON text
        sa.Column("location_lon", sa.Float(), nullable=True),
        sa.Column("location_lat", sa.Float(), nullable=True),
        sa.Column("surface_m2", sa.Float(), nullable=False),
        sa.Column("panel_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Table drones
    op.create_table(
        "drones",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("serial_number", sa.String(100), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="available"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Table inspections
    op.create_table(
        "inspections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("sites.id", ondelete="CASCADE"), nullable=False),
        sa.Column("drone_id", UUID(as_uuid=True), sa.ForeignKey("drones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="planned"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("irradiance_wm2", sa.Float(), nullable=True),
        sa.Column("wind_speed_ms", sa.Float(), nullable=True),
        sa.Column("ambient_temp_c", sa.Float(), nullable=True),
        # Colonnes JSON — remplacent shared/ filesystem sur Render
        sa.Column("anomalies_geojson", JSON(), nullable=True),
        sa.Column("processing_status", JSON(), nullable=True),
        sa.Column("report_data", JSON(), nullable=True),
        sa.Column("work_orders", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Table images
    op.create_table(
        "images",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("inspection_id", UUID(as_uuid=True), sa.ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("image_type", sa.String(10), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("gps_lat", sa.Float(), nullable=True),
        sa.Column("gps_lon", sa.Float(), nullable=True),
        sa.Column("altitude_m", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Table panels
    op.create_table(
        "panels",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("sites.id", ondelete="CASCADE"), nullable=False),
        sa.Column("string_id", sa.String(50), nullable=False),
        sa.Column("row_num", sa.Integer(), nullable=False),
        sa.Column("position_num", sa.Integer(), nullable=False),
        sa.Column("geometry", JSON(), nullable=True),  # GeoJSON Polygon
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Index pour les requêtes fréquentes
    op.create_index("ix_inspections_site_id", "inspections", ["site_id"])
    op.create_index("ix_inspections_status", "inspections", ["status"])
    op.create_index("ix_images_inspection_id", "images", ["inspection_id"])
    op.create_index("ix_panels_site_id", "panels", ["site_id"])


def downgrade() -> None:
    op.drop_table("panels")
    op.drop_table("images")
    op.drop_table("inspections")
    op.drop_table("drones")
    op.drop_table("sites")
    op.execute("DROP EXTENSION IF EXISTS postgis_topology")
    op.execute("DROP EXTENSION IF EXISTS postgis")
