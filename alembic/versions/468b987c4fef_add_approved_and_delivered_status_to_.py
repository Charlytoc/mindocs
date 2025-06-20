"""add APPROVED and DELIVERED status to casestatus enum

Revision ID: 468b987c4fef
Revises: f65248558e91
Create Date: 2025-06-20 09:56:05.119988

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "468b987c4fef"
down_revision: Union[str, Sequence[str], None] = "f65248558e91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from alembic import op

    op.execute("ALTER TYPE casestatus ADD VALUE IF NOT EXISTS 'APPROVED';")
    op.execute("ALTER TYPE casestatus ADD VALUE IF NOT EXISTS 'DELIVERED';")


def downgrade() -> None:
    """Downgrade schema."""
    pass
