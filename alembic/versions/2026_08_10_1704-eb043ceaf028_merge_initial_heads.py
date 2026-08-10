"""merge_initial_heads

Revision ID: eb043ceaf028
Revises: ('001_initial_jobs_table', '001_initial_schema')
Create Date: 2026-08-10 17:04:39.451530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb043ceaf028'
down_revision: Union[str, None] = ('001_initial_jobs_table', '001_initial_schema')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
