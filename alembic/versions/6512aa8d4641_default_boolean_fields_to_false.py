"""Default Boolean fields to False

Revision ID: 6512aa8d4641
Revises: ec1ba2363191
Create Date: 2019-02-27 13:22:03.863516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6512aa8d4641'
down_revision = 'ec1ba2363191'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('task_orders', 'cor_invite', type_=sa.Boolean(), server_default=False)
    op.alter_column('task_orders', 'ko_invite', type_=sa.Boolean(), server_default=False)
    op.alter_column('task_orders', 'so_invite', type_=sa.Boolean(), server_default=False)
    op.alter_column('task_orders', 'unlimited_level_of_warrant', type_=sa.Boolean(), server_default=False)

def downgrade():
    op.alter_column('task_orders', 'cor_invite', type_=sa.Boolean(), server_default=None)
    op.alter_column('task_orders', 'ko_invite', type_=sa.Boolean(), server_default=None)
    op.alter_column('task_orders', 'so_invite', type_=sa.Boolean(), server_default=None)
    op.alter_column('task_orders', 'unlimited_level_of_warrant', type_=sa.Boolean(), server_default=None)
