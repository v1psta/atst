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

    all_roles_but_default = session.query(Role).filter(Role.name != "default").all()
    for role in all_roles_but_default:
        role.add_permission(Permissions.VIEW_WORKSPACE)
        session.add(role)

    owner_and_ccpo = session.query(Role).filter(Role.name.in_(["owner", "ccpo"])).all()
    for role in owner_and_ccpo:
        role.add_permission(Permissions.VIEW_WORKSPACE_MEMBERS)
        session.add(role)

    session.flush()
    session.commit()


def downgrade():
    session = Session(bind=op.get_bind())

    all_roles_but_default = session.query(Role).filter(Role.name != "default").all()
    for role in all_roles_but_default:
        role.remove_permission(Permissions.VIEW_WORKSPACE)
        session.add(role)

    owner_and_ccpo = session.query(Role).filter(Role.name.in_(["owner", "ccpo"])).all()
    for role in owner_and_ccpo:
        role.remove_permission(Permissions.VIEW_WORKSPACE_MEMBERS)
        session.add(role)

    session.flush()
    session.commit()
