from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models import Role, Permissions
from .exceptions import NotFoundError


ATAT_ROLES = [
    {
        "name": "ccpo",
        "display_name": "CCPO",
        "description": "",
        "permissions": [
            Permissions.VIEW_ORIGINAL_JEDI_REQEUST,
            Permissions.REVIEW_AND_APPROVE_JEDI_PORTFOLIO_REQUEST,
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
            Permissions.DEACTIVATE_PORTFOLIO,
            Permissions.VIEW_ATAT_PERMISSIONS,
            Permissions.TRANSFER_OWNERSHIP_OF_PORTFOLIO,
            Permissions.VIEW_PORTFOLIO,
            Permissions.VIEW_PORTFOLIO_MEMBERS,
            Permissions.ADD_APPLICATION_IN_PORTFOLIO,
            Permissions.DELETE_APPLICATION_IN_PORTFOLIO,
            Permissions.DEACTIVATE_APPLICATION_IN_PORTFOLIO,
            Permissions.VIEW_APPLICATION_IN_PORTFOLIO,
            Permissions.RENAME_APPLICATION_IN_PORTFOLIO,
            Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
            Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
            Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
            Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
            Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,
            Permissions.ADD_TAG_TO_PORTFOLIO,
            Permissions.REMOVE_TAG_FROM_PORTFOLIO,
            Permissions.VIEW_AUDIT_LOG,
            Permissions.VIEW_PORTFOLIO_AUDIT_LOG,
        ],
    },
    {
        "name": "default",
        "display_name": "Default",
        "description": "",
        "permissions": [Permissions.REQUEST_JEDI_PORTFOLIO],
    },
]
PORTFOLIO_ROLES = [
    {
        "name": "owner",
        "display_name": "Portfolio Owner",
        "description": "Adds, edits, deactivates access to all applications, environments, and members. Views budget reports. Initiates and edits JEDI Cloud requests.",
        "permissions": [
            Permissions.REQUEST_JEDI_PORTFOLIO,
            Permissions.VIEW_ORIGINAL_JEDI_REQEUST,
            Permissions.VIEW_USAGE_REPORT,
            Permissions.VIEW_USAGE_DOLLARS,
            Permissions.ADD_AND_ASSIGN_CSP_ROLES,
            Permissions.REMOVE_CSP_ROLES,
            Permissions.REQUEST_NEW_CSP_ROLE,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,
            Permissions.DEACTIVATE_PORTFOLIO,
            Permissions.VIEW_ATAT_PERMISSIONS,
            Permissions.VIEW_PORTFOLIO,
            Permissions.VIEW_PORTFOLIO_MEMBERS,
            Permissions.EDIT_PORTFOLIO_INFORMATION,
            Permissions.ADD_APPLICATION_IN_PORTFOLIO,
            Permissions.DELETE_APPLICATION_IN_PORTFOLIO,
            Permissions.DEACTIVATE_APPLICATION_IN_PORTFOLIO,
            Permissions.VIEW_APPLICATION_IN_PORTFOLIO,
            Permissions.RENAME_APPLICATION_IN_PORTFOLIO,
            Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
            Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
            Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
            Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
            Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,
            Permissions.VIEW_PORTFOLIO_AUDIT_LOG,
            Permissions.VIEW_TASK_ORDER,
            Permissions.UPDATE_TASK_ORDER,
            Permissions.ADD_TASK_ORDER_OFFICER,
        ],
    },
    {
        "name": "admin",
        "display_name": "Administrator",
        "description": "Adds and edits applications, environments, members, but cannot deactivate. Cannot view budget reports or JEDI Cloud requests.",
        "permissions": [
            Permissions.VIEW_USAGE_REPORT,
            Permissions.ADD_AND_ASSIGN_CSP_ROLES,
            Permissions.REMOVE_CSP_ROLES,
            Permissions.REQUEST_NEW_CSP_ROLE,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,
            Permissions.VIEW_PORTFOLIO,
            Permissions.VIEW_PORTFOLIO_MEMBERS,
            Permissions.EDIT_PORTFOLIO_INFORMATION,
            Permissions.ADD_APPLICATION_IN_PORTFOLIO,
            Permissions.DELETE_APPLICATION_IN_PORTFOLIO,
            Permissions.DEACTIVATE_APPLICATION_IN_PORTFOLIO,
            Permissions.VIEW_APPLICATION_IN_PORTFOLIO,
            Permissions.RENAME_APPLICATION_IN_PORTFOLIO,
            Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
            Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
            Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
            Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
            Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,
            Permissions.VIEW_PORTFOLIO_AUDIT_LOG,
            Permissions.VIEW_TASK_ORDER,
            Permissions.UPDATE_TASK_ORDER,
            Permissions.ADD_TASK_ORDER_OFFICER,
        ],
    },
    {
        "name": "developer",
        "display_name": "Developer",
        "description": "Views only the applications and environments they are granted access to. Can also view members associated with each environment.",
        "permissions": [Permissions.VIEW_USAGE_REPORT, Permissions.VIEW_PORTFOLIO],
    },
    {
        "name": "billing_auditor",
        "display_name": "Billing Auditor",
        "description": "Views only the applications and environments they are granted access to. Can also view budgets and reports associated with the portfolio.",
        "permissions": [
            Permissions.VIEW_USAGE_REPORT,
            Permissions.VIEW_USAGE_DOLLARS,
            Permissions.VIEW_PORTFOLIO,
        ],
    },
    {
        "name": "security_auditor",
        "description": "Views only the applications and environments they are granted access to. Can also view activity logs.",
        "display_name": "Security Auditor",
        "permissions": [
            Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,
            Permissions.VIEW_ATAT_PERMISSIONS,
            Permissions.VIEW_PORTFOLIO,
        ],
    },
    {
        "name": "officer",
        "description": "Officer involved with setting up a Task Order",
        "display_name": "Task Order Officer",
        "permissions": [
            Permissions.VIEW_PORTFOLIO,
            Permissions.VIEW_USAGE_REPORT,
            Permissions.VIEW_USAGE_DOLLARS,
        ],
    },
]


class Roles(object):
    @classmethod
    def get(cls, role_name):
        try:
            role = db.session.query(Role).filter_by(name=role_name).one()
        except NoResultFound:
            raise NotFoundError("role")

        return role

    @classmethod
    def get_all(cls):
        return db.session.query(Role).all()
