"""enlarge source column from VARCHAR(20) to VARCHAR(50)

Сбер source name 'Сбер (rabota.sber.ru)' is 21 chars, exceeds 20 limit.

Revision ID: 004
Revises: 003
Create Date: 2026-06-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("vacancies", "source", type_=sa.String(50), existing_type=sa.String(20))


def downgrade() -> None:
    op.alter_column("vacancies", "source", type_=sa.String(20), existing_type=sa.String(50))
