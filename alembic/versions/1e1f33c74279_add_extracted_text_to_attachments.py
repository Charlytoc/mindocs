"""add extracted_text to attachments

Revision ID: 1e1f33c74279
Revises: 85a6e4804461
Create Date: 2025-06-20 03:04:51.260946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e1f33c74279'
down_revision: Union[str, Sequence[str], None] = '85a6e4804461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
