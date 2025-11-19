"""Initial schema

Revision ID: c543be6dd922
Revises: ac3d8fcc3e60
Create Date: 2025-11-19 20:54:41.957579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c543be6dd922'
down_revision: Union[str, None] = 'ac3d8fcc3e60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
