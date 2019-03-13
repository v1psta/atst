"""rename roles table to permission_sets

Revision ID: a19138e386c4
Revises: 0e71ab219ada
Create Date: 2019-03-13 10:18:35.770296

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a19138e386c4'
down_revision = '0e71ab219ada'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("roles", "permission_sets")
    op.rename_table("portfolio_roles_roles", "portfolio_roles_permission_sets")
    op.alter_column("portfolio_roles_permission_sets", "role_id", new_column_name="permission_set_id")


def downgrade():
    op.rename_table("permission_sets", "roles")
    op.rename_table("portfolio_roles_permission_sets", "portfolio_roles_roles")
    op.alter_column("portfolio_roles_permission_sets", "permission_set_id", new_column_name="role_id")
