"""add edit workspace information permission

Revision ID: 4c425f17bfe8
Revises: 2572be7fb7fc
Create Date: 2018-09-17 13:14:38.781744

"""
from alembic import op
from sqlalchemy.orm.session import Session

from atst.models.role import Role
from atst.models.permissions import Permissions


# revision identifiers, used by Alembic.
revision = '4c425f17bfe8'
down_revision = '2572be7fb7fc'
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())

    owner_and_admin = session.query(Role).filter(Role.name.in_(["owner", "admin"])).all()
    for role in owner_and_admin:
        role.add_permission(Permissions.EDIT_WORKSPACE_INFORMATION)
        session.add(role)

    session.flush()
    session.commit()


def downgrade():
    session = Session(bind=op.get_bind())

    owner_and_admin = session.query(Role).filter(Role.name.in_(["owner", "admin"])).all()
    for role in owner_and_admin:
        role.remove_permission(Permissions.EDIT_WORKSPACE_INFORMATION)
        session.add(role)

    session.flush()
    session.commit()
