"""full prefix for certifying official on dd 254

Revision ID: fa3ba4049218
Revises: 7d9f070012ae
Create Date: 2019-02-20 11:19:39.655438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa3ba4049218'
down_revision = '7d9f070012ae'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("dd_254s", "co_address", new_column_name="certifying_official_address")
    op.alter_column("dd_254s", "co_phone", new_column_name="certifying_official_phone")
    op.alter_column("dd_254s", "co_title", new_column_name="certifying_official_title")

def downgrade():
    op.alter_column("dd_254s", "certifying_official_address", new_column_name="co_address")
    op.alter_column("dd_254s", "certifying_official_phone", new_column_name="co_phone")
    op.alter_column("dd_254s", "certifying_official_title", new_column_name="co_title")
