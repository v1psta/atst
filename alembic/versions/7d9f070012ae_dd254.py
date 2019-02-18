"""dd254

Revision ID: 7d9f070012ae
Revises: b3a1a07cf30b
Create Date: 2019-02-18 08:38:07.076612

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7d9f070012ae'
down_revision = 'b3a1a07cf30b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('dd_254s',
    sa.Column('time_created', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('time_updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('certifying_official', sa.String(), nullable=True),
    sa.Column('co_title', sa.String(), nullable=True),
    sa.Column('co_address', sa.String(), nullable=True),
    sa.Column('co_phone', sa.String(), nullable=True),
    sa.Column('required_distribution', sa.ARRAY(sa.String()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('task_orders', sa.Column('dd_254_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("task_orders_dd_254s_id", 'task_orders', 'dd_254s', ['dd_254_id'], ['id'])


def downgrade():
    op.drop_constraint('task_orders_dd_254s_id', 'task_orders', type_='foreignkey')
    op.drop_column('task_orders', 'dd_254_id')
    op.drop_table('dd_254s')
