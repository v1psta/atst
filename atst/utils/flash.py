from flask import flash, render_template_string

MESSAGES = {
    "new_workspace_member": {
        "title_template": "Member added successfully",
        "message_template": """
          <p>{{ new_member.user_name }} was successfully invited via email to this workspace. They do not yet have access to any environments.</p>
          <p><a href="{{ url_for('workspaces.update_member', workspace_id=workspace.id, member_id=new_member.user_id) }}">Add environment access.</a></p>
        """,
        "category": "success",
    },
    "revoked_workspace_access": {
        "title_template": "Removed workspace access",
        "message_template": """
          <p>Portfolio access successfully removed from {{ member_name }}.</p>
        """,
        "category": "success",
    },
    "resend_workspace_invitation": {
        "title_template": "Invitation resent",
        "message_template": """
          <p>Successfully sent a new invitation to {{ user_name }}.</p>
        """,
        "category": "success",
    },
    "workspace_role_updated": {
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
    "new_workspace": {
        "title_template": "Portfolio created!",
        "message_template": """
             <p>You are now ready to create applications and environments within the JEDI Cloud.</p>
        """,
        "category": "success",
    },
    "workspace_member_dod_id_error": {
        "title_template": "CAC ID Error",
        "message_template": """
            The member attempted to accept this invite, but their CAC ID did not match the CAC ID you specified on the invite. Please confirm that the DOD ID is accurate.
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
    "request_incomplete": {
        "title_template": "Please complete all sections",
        "message_template": """
            <p>In order to submit your JEDI Cloud request, you'll need to complete all required sections of this form without error. Missing or invalid fields are noted below.</p>
        """,
        "category": "error",
    },
    "requests_action_required": {
        "title_template": "Action required on {{ count }} requests.",
        "message_template": "",
        "category": "info",
    },
    "request_review_comment": {
        "title_template": "Changes Requested",
        "message_template": """
            <p>CCPO has requested changes to your submission with the following notes:
            <br>
            {{ comment }}
            <br>
            Please contact info@jedi.cloud or 123-123-4567 for further discussion.</p>
        """,
        "category": "warning",
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
}


def formatted_flash(message_name, **message_args):
    config = MESSAGES[message_name]
    title = render_template_string(config["title_template"], **message_args)
    message = render_template_string(config["message_template"], **message_args)
    flash({"title": title, "message": message}, config["category"])
