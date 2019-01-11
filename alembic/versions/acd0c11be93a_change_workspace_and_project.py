"""change workspace and project

Revision ID: acd0c11be93a
Revises: 71cbe76c3b87
Create Date: 2019-01-11 10:01:07.667126

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'acd0c11be93a'
down_revision = '71cbe76c3b87'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('audit_events', "workspace_id", new_column_name="portfolio_id")
    op.alter_column('environments', "project_id", new_column_name="application_id")
    op.alter_column('projects', "workspace_id", new_column_name="portfolio_id")
    op.alter_column('task_orders', "workspace_id", new_column_name="portfolio_id")
    op.alter_column('workspace_roles', "workspace_id", new_column_name="portfolio_id")
    op.alter_column('invitations', "workspace_role_id", new_column_name="portfolio_role_id")


def downgrade():
    op.alter_column('audit_events', "portfolio_id", new_column_name="workspace_id")
    op.alter_column('environments', "application_id", new_column_name="project_id")
    op.alter_column('projects', "portfolio_id", new_column_name="workspace_id")
    op.alter_column('task_orders', "portfolio_id", new_column_name="workspace_id")
    op.alter_column('workspace_roles', "portfolio_id", new_column_name="workspace_id")
    op.alter_column('invitations', "portfolio_role_id", new_column_name="workspace_role_id")
