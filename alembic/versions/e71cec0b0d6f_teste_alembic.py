"""teste alembic

Revision ID: e71cec0b0d6f
Revises: 7cee1d785e76
Create Date: 2026-07-22 14:28:14.531755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e71cec0b0d6f'
down_revision: Union[str, Sequence[str], None] = '7cee1d785e76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
