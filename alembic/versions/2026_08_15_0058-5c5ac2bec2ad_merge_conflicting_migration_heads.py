"""merge conflicting migration heads

Revision ID: 5c5ac2bec2ad
Revises: ee238d53544e
Create Date: 2026-08-15 00:58:53.426682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c5ac2bec2ad'
down_revision: Union[str, None] = 'ee238d53544e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
