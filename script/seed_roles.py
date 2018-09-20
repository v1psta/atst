# Add root project dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from sqlalchemy.orm.exc import NoResultFound
from atst.app import make_config, make_app
from atst.database import db
from atst.models import Role, Permissions

roles = [
    Role(
        name="ccpo",
        display_name="CCPO",
        description="",
        permissions=[
            Permissions.VIEW_ORIGINAL_JEDI_REQEUST,
            Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST,
            Permissions.MODIFY_ATAT_ROLE_PERMISSIONS,
            Permissions.CREATE_CSP_ROLE,
            Permissions.DELETE_CSP_ROLE,
            Permissions.DEACTIVE_CSP_ROLE,
            Permissions.MODIFY_CSP_ROLE_PERMISSIONS,
            Permissions.VIEW_USAGE_REPORT,
            Permissions.VIEW_USAGE_DOLLARS,
            Permissions.ADD_AND_ASSIGN_CSP_ROLES,
            Permissions.REMOVE_CSP_ROLES,
            Permissions.REQUEST_NEW_CSP_ROLE,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,
            Permissions.DEACTIVATE_WORKSPACE,
            Permissions.VIEW_ATAT_PERMISSIONS,
            Permissions.TRANSFER_OWNERSHIP_OF_WORKSPACE,
            Permissions.VIEW_WORKSPACE,
            Permissions.VIEW_WORKSPACE_MEMBERS,
            Permissions.ADD_APPLICATION_IN_WORKSPACE,
            Permissions.DELETE_APPLICATION_IN_WORKSPACE,
            Permissions.DEACTIVATE_APPLICATION_IN_WORKSPACE,
            Permissions.VIEW_APPLICATION_IN_WORKSPACE,
            Permissions.RENAME_APPLICATION_IN_WORKSPACE,
            Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
            Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
            Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
            Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
            Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,
            Permissions.ADD_TAG_TO_WORKSPACE,
            Permissions.REMOVE_TAG_FROM_WORKSPACE,
            Permissions.VIEW_AUDIT_LOG
        ],
    ),
    Role(
        name="owner",
        display_name="Owner",
        description="",
        permissions=[
            Permissions.REQUEST_JEDI_WORKSPACE,
            Permissions.VIEW_ORIGINAL_JEDI_REQEUST,
            Permissions.VIEW_USAGE_REPORT,
            Permissions.VIEW_USAGE_DOLLARS,
            Permissions.ADD_AND_ASSIGN_CSP_ROLES,
            Permissions.REMOVE_CSP_ROLES,
            Permissions.REQUEST_NEW_CSP_ROLE,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,
            Permissions.DEACTIVATE_WORKSPACE,
            Permissions.VIEW_ATAT_PERMISSIONS,
            Permissions.VIEW_WORKSPACE,
            Permissions.VIEW_WORKSPACE_MEMBERS,
            Permissions.EDIT_WORKSPACE_INFORMATION,
            Permissions.ADD_APPLICATION_IN_WORKSPACE,
            Permissions.DELETE_APPLICATION_IN_WORKSPACE,
            Permissions.DEACTIVATE_APPLICATION_IN_WORKSPACE,
            Permissions.VIEW_APPLICATION_IN_WORKSPACE,
            Permissions.RENAME_APPLICATION_IN_WORKSPACE,
            Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
            Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
            Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
            Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
            Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,
        ],
    ),
    Role(
        name="admin",
        display_name="Admin",
        description="",
        permissions=[
            Permissions.VIEW_USAGE_REPORT,
            Permissions.ADD_AND_ASSIGN_CSP_ROLES,
            Permissions.REMOVE_CSP_ROLES,
            Permissions.REQUEST_NEW_CSP_ROLE,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,
            Permissions.VIEW_WORKSPACE,
            Permissions.VIEW_WORKSPACE_MEMBERS,
            Permissions.EDIT_WORKSPACE_INFORMATION,
            Permissions.ADD_APPLICATION_IN_WORKSPACE,
            Permissions.DELETE_APPLICATION_IN_WORKSPACE,
            Permissions.DEACTIVATE_APPLICATION_IN_WORKSPACE,
            Permissions.VIEW_APPLICATION_IN_WORKSPACE,
            Permissions.RENAME_APPLICATION_IN_WORKSPACE,
            Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
            Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
            Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
            Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
            Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,
        ],
    ),
    Role(
        name="developer",
        display_name="Developer",
        description="",
        permissions=[
            Permissions.VIEW_USAGE_REPORT,
            Permissions.VIEW_USAGE_DOLLARS,
            Permissions.VIEW_WORKSPACE,
            Permissions.VIEW_APPLICATION_IN_WORKSPACE,
        ],
    ),
    Role(
        name="billing_auditor",
        display_name="Billing Auditor",
        description="",
        permissions=[
            Permissions.VIEW_USAGE_REPORT,
            Permissions.VIEW_USAGE_DOLLARS,
            Permissions.VIEW_WORKSPACE,
            Permissions.VIEW_APPLICATION_IN_WORKSPACE,
        ],
    ),
    Role(
        name="security_auditor",
        description="",
        display_name="Security Auditor",
        permissions=[
            Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ATAT_PERMISSIONS,
            Permissions.VIEW_WORKSPACE,
            Permissions.VIEW_APPLICATION_IN_WORKSPACE,
        ],
    ),
    Role(
        name="default",
        display_name="Default",
        description="",
        permissions=[Permissions.REQUEST_JEDI_WORKSPACE],
    ),
]


def seed_roles():
    for role in roles:
        try:
            existing_role = db.session.query(Role).filter_by(name=role.name).one()
            existing_role.description = role.description
            existing_role.permissions = role.permissions
            db.session.add(existing_role)
            print("Updated existing role {}".format(existing_role.name))
        except NoResultFound:
            db.session.add(role)
            print("Added new role {}".format(role.name))

    db.session.commit()


if __name__ == "__main__":
    config = make_config()
    app = make_app(config)
    with app.app_context():
        seed_roles()
