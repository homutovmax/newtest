"""create vacancies table

Revision ID: 001
Revises:
Create Date: 2026-06-25
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "vacancies",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("company", sa.String(500), nullable=True),
        sa.Column("salary", sa.String(200), nullable=True),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("category", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), server_default="new"),
        sa.Column("cover_text", sa.Text, nullable=True),
        sa.Column("first_seen", sa.Date, nullable=False),
        sa.Column("last_seen", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("vacancies")
