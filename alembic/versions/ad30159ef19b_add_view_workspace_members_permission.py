"""add view_workspace_members_permission

Revision ID: ad30159ef19b
Revises: 2c2a2af465d3
Create Date: 2018-09-05 11:17:17.204089

"""
from alembic import op
from sqlalchemy.orm.session import Session
from atst.models.role import Role
from atst.models.permissions import Permissions


# revision identifiers, used by Alembic.
revision = 'ad30159ef19b'
down_revision = '06aa23166ca9'
branch_labels = None
depends_on = None

def upgrade():

    session = Session(bind=op.get_bind())

    owner_role = session.query(Role).filter_by(name="owner").one()
    owner_role.permissions.append(Permissions.VIEW_WORKSPACE_MEMBERS)

    ccpo_role = session.query(Role).filter_by(name="ccpo").one()
    ccpo_role.permissions.append(Permissions.VIEW_WORKSPACE_MEMBERS)


def downgrade():
    pass
