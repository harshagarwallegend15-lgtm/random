"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("height_cm", sa.Float, nullable=False),
        sa.Column("weight_kg", sa.Float, nullable=False),
        sa.Column("age", sa.Integer, nullable=False),
        sa.Column("gender", sa.String(16), nullable=False),
        sa.Column("target_weight_kg", sa.Float, nullable=False),
        sa.Column("budget_inr", sa.Float, nullable=False, server_default="3000"),
        sa.Column("city", sa.String(64), nullable=False),
        sa.Column("vegetarian", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("gym_available", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("schedule", sa.String(256), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "photos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("angle", sa.String(16), nullable=False),
        sa.Column("cloudinary_url", sa.String(512), nullable=False),
        sa.Column("cloudinary_public_id", sa.String(256), nullable=False),
        sa.Column("set_id", sa.Integer, index=True),
        sa.Column("landmarks", postgresql.JSONB, nullable=True),
        sa.Column("taken_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("photo_set_id", sa.Integer, index=True),
        sa.Column("body_fat_pct", sa.Float, nullable=False),
        sa.Column("muscle_mass_kg", sa.Float, nullable=False),
        sa.Column("lean_mass_kg", sa.Float, nullable=False),
        sa.Column("posture_score", sa.Float, nullable=False),
        sa.Column("weak_muscles", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("fat_distribution", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("notes", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "roadmaps",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("week", sa.Integer, nullable=False),
        sa.Column("calories", sa.Float, nullable=False),
        sa.Column("protein_g", sa.Float, nullable=False),
        sa.Column("carbs_g", sa.Float, nullable=False),
        sa.Column("fats_g", sa.Float, nullable=False),
        sa.Column("workout_focus", sa.String(128), nullable=False, server_default=""),
        sa.Column("notes", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "workout_plans",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("roadmap_id", sa.Integer, sa.ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True),
        sa.Column("day", sa.Integer, nullable=False),
        sa.Column("title", sa.String(64), nullable=False, server_default=""),
        sa.Column("exercises", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
    )

    op.create_table(
        "grocery_lists",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("roadmap_id", sa.Integer, sa.ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True),
        sa.Column("week", sa.Integer, nullable=False),
        sa.Column("total_inr", sa.Float, nullable=False),
        sa.Column("items", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
    )


def downgrade() -> None:
    for tbl in ("grocery_lists", "workout_plans", "roadmaps", "analyses", "photos", "users"):
        op.drop_table(tbl)
