"""remove view project and environment permissions

Revision ID: dea6b8e09d63
Revises: ad30159ef19b
Create Date: 2018-09-10 11:06:00.017222

"""
from alembic import op
from sqlalchemy.orm.session import Session

from atst.models.role import Role
from atst.models.permissions import Permissions


# revision identifiers, used by Alembic.
revision = "dea6b8e09d63"
down_revision = "ad30159ef19b"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())

    priveleged_role_names = ("owner", "admin", "ccpo")
    non_priveleged_roles = (
        session.query(Role).filter(Role.name.notin_(priveleged_role_names)).all()
    )
    for role in non_priveleged_roles:
        role.remove_permission(Permissions.VIEW_APPLICATION_IN_WORKSPACE)
        role.remove_permission(Permissions.VIEW_ENVIRONMENT_IN_APPLICATION)
        session.add(role)

    session.commit()


def downgrade():
    session = Session(bind=op.get_bind())

    priveleged_role_names = ("owner", "admin", "ccpo")
    non_priveleged_roles = (
        session.query(Role).filter(not Role.name.in_(priveleged_role_names)).all()
    )
    for role in non_priveleged_roles:
        role.add_permission(Permissions.VIEW_APPLICATION_IN_WORKSPACE)
        role.add_permission(Permissions.VIEW_ENVIRONMENT_IN_APPLICATION)
        session.add(role)

    session.commit()
