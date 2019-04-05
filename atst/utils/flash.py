from flask import flash, render_template_string
from atst.utils.localization import translate

MESSAGES = {
    "invitation_resent": {
        "title_template": "Invitation resent",
        "message_template": "The {{ officer_type }}  has been resent instructions to join this portfolio.",
        "category": "success",
    },
    "task_order_draft": {
        "title_template": translate("task_orders.form.draft_alert_title"),
        "message_template": """
        <p>Please complete your task order before submitting it for approval.</p>
        """,
        "category": "warning",
    },
    "task_order_signed": {
        "title_template": "Task Order Signed",
        "message_template": """
        <p>Task order has been signed successfully</p>
        """,
        "category": "success",
    },
    "update_portfolio_members": {
        "title_template": "Success!",
        "message_template": """
            <p>You have successfully updated access permissions for members of {{ portfolio.name }}.</p>
        """,
        "category": "success",
    },
    "new_portfolio_member": {
        "title_template": translate("flash.success"),
        "message_template": """
          <p>{{ "flash.new_portfolio_member" | translate({ "user_name": new_member.user_name }) }}</p>
        """,
        "category": "success",
    },
    "revoked_portfolio_access": {
        "title_template": "Removed portfolio access",
        "message_template": """
          <p>Portfolio access successfully removed from {{ member_name }}.</p>
        """,
        "category": "success",
    },
    "resend_portfolio_invitation": {
        "title_template": "Invitation resent",
        "message_template": """
          <p>Successfully sent a new invitation to {{ user_name }}.</p>
        """,
        "category": "success",
    },
    "portfolio_role_updated": {
        "title_template": "Portfolio role updated successfully",
        "message_template": """
          <p>{{ member_name }}'s role  was successfully updated to {{ updated_role }}</p>
        """,
        "category": "success",
    },
    "session_expired": {
        "title_template": "Session Expired",
        "message_template": """
            Your session expired due to inactivity. Please log in again to continue.
        """,
        "category": "error",
    },
    "login_next": {
        "title_template": "Log in Required.",
        "message_template": """
            After you log in, you will be redirected to your destination page.
        """,
        "category": "warning",
    },
    "new_portfolio": {
        "title_template": "Portfolio created!",
        "message_template": """
             <p>You are now ready to create applications and environments within the JEDI Cloud.</p>
        """,
        "category": "success",
    },
    "portfolio_member_dod_id_error": {
        "title_template": "CAC ID Error",
        "message_template": """
            The member attempted to accept this invite, but their CAC ID did not match the CAC ID you specified on the invite. Please confirm that the DoD ID is accurate.
        """,
        "category": "error",
    },
    "form_errors": {
        "title_template": "There were some errors",
        "message_template": "<p>Please see below.</p>",
        "category": "error",
    },
    "user_must_complete_profile": {
        "title_template": "You must complete your profile",
        "message_template": "<p>Before continuing, you must complete your profile</p>",
        "category": "info",
    },
    "user_updated": {
        "title_template": "User information updated.",
        "message_template": "",
        "category": "success",
    },
    "environment_access_changed": {
        "title_template": "User access successfully changed.",
        "message_template": "",
        "category": "success",
    },
    "task_order_submitted": {
        "title_template": "Task Order Form Submitted",
        "message_template": """
        Your task order form for {{ task_order.portfolio_name }} has been submitted.
        """,
        "category": "success",
    },
    "task_order_congrats": {
        "title_template": translate("flash.congrats"),
        "message_template": translate("flash.new_portfolio"),
        "actions": """
            {% from "components/icon.html" import Icon %}
            <div class='alert__actions'>
              <a href='{{ url_for("portfolios.show_portfolio", portfolio_id=portfolio.id) }}' class='icon-link'>
                {{ Icon('shield') }}
                <span>{{ "flash.portfolio_home" | translate }}</span>
              </a>
              <a href='#next-steps' class='icon-link'>
                {{ Icon('arrow-down') }}
                <span>{{ "flash.next_steps" | translate }}</span>
              </a>
            </div>
        """,
        "category": "success",
    },
    "task_order_incomplete": {
        "title_template": "Task Order Incomplete",
        "message_template": """
        You must complete your task order form before submitting.
        """,
        "category": "error",
    },
    "portfolio_member_removed": {
        "title_template": translate("flash.deleted_member"),
        "message_template": """
            {{ "flash.delete_member_success" | translate({ "member_name": member_name }) }}
        """,
        "category": "success",
    },
}


def formatted_flash(message_name, **message_args):
    config = MESSAGES[message_name]
    title = render_template_string(config["title_template"], **message_args)
    message = render_template_string(config["message_template"], **message_args)
    actions = None
    if "actions" in config:
        actions = render_template_string(config["actions"], **message_args)
    flash({"title": title, "message": message, "actions": actions}, config["category"])
