"""change company to Text

Revision ID: 002
Revises: 001
Create Date: 2026-06-25
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("vacancies", "company", type_=sa.Text, existing_type=sa.String(500))


def downgrade():
    op.alter_column("vacancies", "company", type_=sa.String(500), existing_type=sa.Text)
