class Permissions(object):
    VIEW_AUDIT_LOG = "view_audit_log"
    VIEW_PORTFOLIO_AUDIT_LOG = "view_portfolio_audit_log"
    REQUEST_JEDI_PORTFOLIO = "request_jedi_portfolio"
    VIEW_ORIGINAL_JEDI_REQEUST = "view_original_jedi_request"
    REVIEW_AND_APPROVE_JEDI_PORTFOLIO_REQUEST = (
        "review_and_approve_jedi_portfolio_request"
    )
    MODIFY_ATAT_ROLE_PERMISSIONS = "modify_atat_role_permissions"
    CREATE_CSP_ROLE = "create_csp_role"
    DELETE_CSP_ROLE = "delete_csp_role"
    DEACTIVE_CSP_ROLE = "deactivate_csp_role"
    MODIFY_CSP_ROLE_PERMISSIONS = "modify_csp_role_permissions"

    VIEW_USAGE_REPORT = "view_usage_report"
    VIEW_USAGE_DOLLARS = "view_usage_dollars"
    ADD_AND_ASSIGN_CSP_ROLES = "add_and_assign_csp_roles"
    REMOVE_CSP_ROLES = "remove_csp_roles"
    REQUEST_NEW_CSP_ROLE = "request_new_csp_role"
    ASSIGN_AND_UNASSIGN_ATAT_ROLE = "assign_and_unassign_atat_role"

    VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS = "view_assigned_atat_role_configurations"
    VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS = "view_assigned_csp_role_configurations"

    EDIT_PORTFOLIO_INFORMATION = "edit_portfolio_information"
    DEACTIVATE_PORTFOLIO = "deactivate_portfolio"
    VIEW_ATAT_PERMISSIONS = "view_atat_permissions"
    TRANSFER_OWNERSHIP_OF_PORTFOLIO = "transfer_ownership_of_portfolio"
    VIEW_PORTFOLIO_MEMBERS = "view_portfolio_members"

    ADD_APPLICATION_IN_PORTFOLIO = "add_application_in_portfolio"
    DELETE_APPLICATION_IN_PORTFOLIO = "delete_application_in_portfolio"
    DEACTIVATE_APPLICATION_IN_PORTFOLIO = "deactivate_application_in_portfolio"
    VIEW_APPLICATION_IN_PORTFOLIO = "view_application_in_portfolio"
    RENAME_APPLICATION_IN_PORTFOLIO = "rename_application_in_portfolio"

    ADD_ENVIRONMENT_IN_APPLICATION = "add_environment_in_application"
    DELETE_ENVIRONMENT_IN_APPLICATION = "delete_environment_in_application"
    DEACTIVATE_ENVIRONMENT_IN_APPLICATION = "deactivate_environment_in_application"
    VIEW_ENVIRONMENT_IN_APPLICATION = "view_environment_in_application"
    RENAME_ENVIRONMENT_IN_APPLICATION = "rename_environment_in_application"

    ADD_TAG_TO_PORTFOLIO = "add_tag_to_portfolio"
    REMOVE_TAG_FROM_PORTFOLIO = "remove_tag_from_portfolio"

    VIEW_TASK_ORDER = "view_task_order"
    UPDATE_TASK_ORDER = "update_task_order"
    ADD_TASK_ORDER_OFFICER = "add_task_order_officers"

    # new portfolio permissions
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
