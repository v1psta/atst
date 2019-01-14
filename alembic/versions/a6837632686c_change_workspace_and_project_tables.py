"""change workspace and project tables

Revision ID: a6837632686c
Revises: acd0c11be93a
Create Date: 2019-01-11 10:36:55.030308

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a6837632686c'
down_revision = 'acd0c11be93a'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("workspaces", "portfolios")
    op.rename_table("projects", "applications")
    op.rename_table("workspace_roles", "portfolio_roles")


def downgrade():
    op.rename_table("portfolios", "workspaces")
    op.rename_table("applications", "projects")
    op.rename_table("portfolio_roles", "workspace_roles")
