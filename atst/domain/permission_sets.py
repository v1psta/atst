from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models import PermissionSet, Permissions
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

_VIEW_PORTFOLIO_PERMISSION_SETS = [
    {
        "name": "view_portfolio",
        "description": "View basic portfolio info",
        "display_name": "View Portfolio",
        "permissions": [Permissions.VIEW_PORTFOLIO],
    },
    {
        "name": "view_portfolio_application_management",
        "description": "View applications and related resources",
        "display_name": "Application Management",
        "permissions": [
            Permissions.VIEW_APPLICATION,
            Permissions.VIEW_APPLICATION_MEMBER,
            Permissions.VIEW_ENVIRONMENT,
        ],
    },
    {
        "name": "view_portfolio_funding",
        "description": "View a portfolio's task orders",
        "display_name": "Funding",
        "permissions": [
            Permissions.VIEW_PORTFOLIO_FUNDING,
            Permissions.VIEW_TASK_ORDER_DETAILS,
        ],
    },
    {
        "name": "view_portfolio_reports",
        "description": "View a portfolio's reports",
        "display_name": "Reporting",
        "permissions": [Permissions.VIEW_PORTFOLIO_REPORTS],
    },
    {
        "name": "view_portfolio_admin",
        "description": "View a portfolio's admin options",
        "display_name": "Portfolio Administration",
        "permissions": [
            Permissions.VIEW_PORTFOLIO_ADMIN,
            Permissions.VIEW_PORTFOLIO_NAME,
            Permissions.VIEW_PORTFOLIO_USERS,
            Permissions.VIEW_PORTFOLIO_ACTIVITY_LOG,
            Permissions.VIEW_PORTFOLIO_POC,
        ],
    },
]

_EDIT_PORTFOLIO_PERMISSION_SETS = [
    {
        "name": "edit_portfolio_application_management",
        "description": "Edit applications and related resources",
        "display_name": "Application Management",
        "permissions": [
            Permissions.EDIT_APPLICATION,
            Permissions.CREATE_APPLICATION,
            Permissions.EDIT_APPLICATION_MEMBER,
            Permissions.CREATE_APPLICATION_MEMBER,
            Permissions.EDIT_ENVIRONMENT,
            Permissions.CREATE_ENVIRONMENT,
        ],
    },
    {
        "name": "edit_portfolio_funding",
        "description": "Edit a portfolio's task orders and add new ones",
        "display_name": "Funding",
        "permissions": [
            Permissions.CREATE_TASK_ORDER,
            Permissions.EDIT_TASK_ORDER_DETAILS,
        ],
    },
    {
        "name": "edit_portfolio_reports",
        "description": "Edit a portfolio's reports (no-op)",
        "display_name": "Reporting",
        "permissions": [],
    },
    {
        "name": "edit_portfolio_admin",
        "description": "Edit a portfolio's admin options",
        "display_name": "Portfolio Administration",
        "permissions": [
            Permissions.EDIT_PORTFOLIO_NAME,
            Permissions.EDIT_PORTFOLIO_USERS,
            Permissions.CREATE_PORTFOLIO_USERS,
        ],
    },
]

PORTFOLIO_PERMISSION_SETS = (
    _VIEW_PORTFOLIO_PERMISSION_SETS
    + _EDIT_PORTFOLIO_PERMISSION_SETS
    + [
        {
            "name": "portfolio_poc",
            "description": "Permissions belonging to the Portfolio POC",
            "display_name": "Portfolio Point of Contact",
            "permissions": [
                Permissions.EDIT_PORTFOLIO_POC,
                Permissions.ARCHIVE_PORTFOLIO,
            ],
        }
    ]
)


class PermissionSets(object):
    @classmethod
    def get(cls, perms_set_name):
        try:
            role = db.session.query(PermissionSet).filter_by(name=perms_set_name).one()
        except NoResultFound:
            raise NotFoundError("permission_set")

        return role

    @classmethod
    def get_all(cls):
        return db.session.query(PermissionSet).all()
