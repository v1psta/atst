from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models import PermissionSet, Permissions
from .exceptions import NotFoundError


class PermissionSets(object):
    VIEW_PORTFOLIO = "view_portfolio"
    VIEW_PORTFOLIO_APPLICATION_MANAGEMENT = "view_portfolio_application_management"
    VIEW_PORTFOLIO_FUNDING = "view_portfolio_funding"
    VIEW_PORTFOLIO_REPORTS = "view_portfolio_reports"
    VIEW_PORTFOLIO_ADMIN = "view_portfolio_admin"
    EDIT_PORTFOLIO_APPLICATION_MANAGEMENT = "edit_portfolio_application_management"
    EDIT_PORTFOLIO_FUNDING = "edit_portfolio_funding"
    EDIT_PORTFOLIO_REPORTS = "edit_portfolio_reports"
    EDIT_PORTFOLIO_ADMIN = "edit_portfolio_admin"
    PORTFOLIO_POC = "portfolio_poc"

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

    @classmethod
    def get_many(cls, perms_set_names):
        return (
            db.session.query(PermissionSet)
            .filter(PermissionSet.name.in_(perms_set_names))
            .all()
        )


ATAT_ROLES = [
    {
        "name": "ccpo",
        "display_name": "CCPO",
        "description": "",
        "permissions": [Permissions.VIEW_AUDIT_LOG],
    },
    {
        "name": "default",
        "display_name": "Default",
        "description": "",
        "permissions": [],
    },
]

_PORTFOLIO_BASIC_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO,
        "description": "View basic portfolio info",
        "display_name": "View Portfolio",
        "permissions": [Permissions.VIEW_PORTFOLIO],
    }
]

_PORTFOLIO_APP_MGMT_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
        "description": "View applications and related resources",
        "display_name": "Application Management",
        "permissions": [
            Permissions.VIEW_APPLICATION,
            Permissions.VIEW_APPLICATION_MEMBER,
            Permissions.VIEW_ENVIRONMENT,
        ],
    },
    {
        "name": PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
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
]

_PORTFOLIO_FUNDING_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO_FUNDING,
        "description": "View a portfolio's task orders",
        "display_name": "Funding",
        "permissions": [
            Permissions.VIEW_PORTFOLIO_FUNDING,
            Permissions.VIEW_TASK_ORDER_DETAILS,
        ],
    },
    {
        "name": PermissionSets.EDIT_PORTFOLIO_FUNDING,
        "description": "Edit a portfolio's task orders and add new ones",
        "display_name": "Funding",
        "permissions": [
            Permissions.CREATE_TASK_ORDER,
            Permissions.EDIT_TASK_ORDER_DETAILS,
        ],
    },
]

_PORTFOLIO_REPORTS_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO_REPORTS,
        "description": "View a portfolio's reports",
        "display_name": "Reporting",
        "permissions": [Permissions.VIEW_PORTFOLIO_REPORTS],
    },
    {
        "name": PermissionSets.EDIT_PORTFOLIO_REPORTS,
        "description": "Edit a portfolio's reports (no-op)",
        "display_name": "Reporting",
        "permissions": [],
    },
]

_PORTFOLIO_ADMIN_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO_ADMIN,
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
    {
        "name": PermissionSets.EDIT_PORTFOLIO_ADMIN,
        "description": "Edit a portfolio's admin options",
        "display_name": "Portfolio Administration",
        "permissions": [
            Permissions.EDIT_PORTFOLIO_NAME,
            Permissions.EDIT_PORTFOLIO_USERS,
            Permissions.CREATE_PORTFOLIO_USERS,
        ],
    },
]

_PORTFOLIO_POC_PERMISSION_SETS = [
    {
        "name": "portfolio_poc",
        "description": "Permissions belonging to the Portfolio POC",
        "display_name": "Portfolio Point of Contact",
        "permissions": [Permissions.EDIT_PORTFOLIO_POC, Permissions.ARCHIVE_PORTFOLIO],
    }
]

PORTFOLIO_PERMISSION_SETS = (
    _PORTFOLIO_BASIC_PERMISSION_SETS
    + _PORTFOLIO_APP_MGMT_PERMISSION_SETS
    + _PORTFOLIO_FUNDING_PERMISSION_SETS
    + _PORTFOLIO_REPORTS_PERMISSION_SETS
    + _PORTFOLIO_ADMIN_PERMISSION_SETS
    + _PORTFOLIO_POC_PERMISSION_SETS
)
