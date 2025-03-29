"""change_user_document_to_many_to_many

Revision ID: 888286bdccdc
Revises: e372e2cb352f
Create Date: 2025-03-27 20:49:34.795675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '888286bdccdc'
down_revision: Union[str, None] = 'e372e2cb352f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
