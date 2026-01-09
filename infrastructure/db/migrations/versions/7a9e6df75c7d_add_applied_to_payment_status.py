"""add applied to payment_status

Revision ID: 7a9e6df75c7d
Revises: f069f1240bc6
Create Date: 2026-01-06 16:58:57.184076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a9e6df75c7d'
down_revision: Union[str, Sequence[str], None] = 'f069f1240bc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE payment_status ADD VALUE IF NOT EXISTS 'applied'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
