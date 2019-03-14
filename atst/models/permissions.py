class Permissions(object):
    VIEW_AUDIT_LOG = "view_audit_log"

    # base portfolio perms
    VIEW_PORTFOLIO = "view_portfolio"

    # application management
    VIEW_APPLICATION = "view_application"
    EDIT_APPLICATION = "edit_application"
    CREATE_APPLICATION = "create_application"
    VIEW_APPLICATION_MEMBER = "view_application_member"
    EDIT_APPLICATION_MEMBER = "edit_application_member"
    CREATE_APPLICATION_MEMBER = "create_application_member"
    VIEW_ENVIRONMENT = "view_environment"
    EDIT_ENVIRONMENT = "edit_environment"
    CREATE_ENVIRONMENT = "create_environment"

    # funding
    VIEW_PORTFOLIO_FUNDING = "view_portfolio_funding"  # TO summary page
    CREATE_TASK_ORDER = "create_task_order"  # create a new TO
    VIEW_TASK_ORDER_DETAILS = "view_task_order_details"  # individual TO page
    EDIT_TASK_ORDER_DETAILS = (
        "edit_task_order_details"
    )  # edit TO that has not been finalized

    # reporting
    VIEW_PORTFOLIO_REPORTS = "view_portfolio_reports"

    # portfolio admin
    VIEW_PORTFOLIO_ADMIN = "view_portfolio_admin"
    VIEW_PORTFOLIO_NAME = "view_portfolio_name"
    EDIT_PORTFOLIO_NAME = "edit_portfolio_name"
    VIEW_PORTFOLIO_USERS = "view_portfolio_users"
    EDIT_PORTFOLIO_USERS = "edit_portfolio_users"
    CREATE_PORTFOLIO_USERS = "create_portfolio_users"
    VIEW_PORTFOLIO_ACTIVITY_LOG = "view_portfolio_activity_log"
    VIEW_PORTFOLIO_POC = "view_portfolio_poc"

    # portfolio POC
    EDIT_PORTFOLIO_POC = "edit_portfolio_poc"
    ARCHIVE_PORTFOLIO = "archive_portfolio"
