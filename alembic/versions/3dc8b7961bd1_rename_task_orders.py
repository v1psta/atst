"""rename task orders

Revision ID: 3dc8b7961bd1
Revises: 02d11579a581
Create Date: 2018-12-12 13:17:25.728679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3dc8b7961bd1'
down_revision = '02d11579a581'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("task_orders", "legacy_task_orders")


def downgrade():
    op.rename_table("legacy_task_orders", "task_orders")
