"""Ajout colonnes wizard sur inspections + table inspection_images.

Revision ID: 003
Revises: 002
Create Date: 2026-03-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Nouvelles colonnes sur la table inspections
    # ------------------------------------------------------------------
    new_inspection_columns = [
        ("org_id", sa.Column("org_id", UUID(as_uuid=True), nullable=True)),
        ("plan_type", sa.Column("plan_type", sa.String(30), nullable=True, server_default="professional_5gsd")),
        ("gsd_target_cm", sa.Column("gsd_target_cm", sa.Float(), nullable=True, server_default="5.0")),
        ("drone_manufacturer", sa.Column("drone_manufacturer", sa.String(100), nullable=True)),
        ("drone_model", sa.Column("drone_model", sa.String(100), nullable=True)),
        ("drone_serial_number", sa.Column("drone_serial_number", sa.String(100), nullable=True)),
        ("service_fee_usd", sa.Column("service_fee_usd", sa.Float(), nullable=True)),
        ("bank_commission_pct", sa.Column("bank_commission_pct", sa.Float(), nullable=True, server_default="5.0")),
        ("total_amount_usd", sa.Column("total_amount_usd", sa.Float(), nullable=True)),
        ("payment_status", sa.Column("payment_status", sa.String(20), nullable=True, server_default="pending")),
        ("progression", sa.Column("progression", sa.Integer(), nullable=True, server_default="0")),
        ("flight_date", sa.Column("flight_date", sa.Date(), nullable=True)),
        ("weather_conditions", sa.Column("weather_conditions", JSON, nullable=True)),
        ("updated_at", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)),
        ("work_orders", sa.Column("work_orders", JSON, nullable=True)),
    ]

    for col_name, col_def in new_inspection_columns:
        try:
            op.add_column("inspections", col_def)
        except Exception:
            # Colonne déjà présente — ignorer
            pass

    # Migrer l'ancienne colonne status (PLANNED/IN_PROGRESS/…) vers les nouveaux
    # statuts IEC — on laisse les valeurs en place ; le modèle accepte les deux.
    # Aucune transformation destructive ici.

    # ------------------------------------------------------------------
    # Nouvelle table inspection_images
    # ------------------------------------------------------------------
    op.create_table(
        "inspection_images",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "inspection_id",
            UUID(as_uuid=True),
            sa.ForeignKey("inspections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("image_type", sa.String(20), nullable=False, server_default="rgb"),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("storage_url", sa.String(1000), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("gps_latitude", sa.Float(), nullable=True),
        sa.Column("gps_longitude", sa.Float(), nullable=True),
        sa.Column("gps_altitude_m", sa.Float(), nullable=True),
        sa.Column("capture_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exif_data", JSON, nullable=True),
        sa.Column("processing_status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_inspection_images_inspection_id",
        "inspection_images",
        ["inspection_id"],
    )
    op.create_index(
        "ix_inspection_images_image_type",
        "inspection_images",
        ["image_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_inspection_images_image_type", table_name="inspection_images")
    op.drop_index("ix_inspection_images_inspection_id", table_name="inspection_images")
    op.drop_table("inspection_images")

    columns_to_drop = [
        "org_id",
        "plan_type",
        "gsd_target_cm",
        "drone_manufacturer",
        "drone_model",
        "drone_serial_number",
        "service_fee_usd",
        "bank_commission_pct",
        "total_amount_usd",
        "payment_status",
        "progression",
        "flight_date",
        "weather_conditions",
        "updated_at",
        "work_orders",
    ]
    for col_name in columns_to_drop:
        try:
            op.drop_column("inspections", col_name)
        except Exception:
            pass
