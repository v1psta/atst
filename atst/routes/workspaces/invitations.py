from flask import g, redirect, url_for, render_template

from . import workspaces_bp
from atst.domain.workspaces import Workspaces
from atst.domain.invitations import Invitations
from atst.queue import queue
from atst.utils.flash import formatted_flash as flash


def send_invite_email(owner_name, token, new_member_email):
    body = render_template("emails/invitation.txt", owner=owner_name, token=token)
    queue.send_mail(
        [new_member_email],
        "{} has invited you to a JEDI Cloud Workspace".format(owner_name),
        body,
    )


@workspaces_bp.route("/workspaces/invitations/<token>", methods=["GET"])
def accept_invitation(token):
    invite = Invitations.accept(g.current_user, token)

    return redirect(
        url_for("workspaces.show_workspace", workspace_id=invite.workspace.id)
    )


@workspaces_bp.route(
    "/workspaces/<workspace_id>/invitations/<token>/revoke", methods=["POST"]
)
def revoke_invitation(workspace_id, token):
    workspace = Workspaces.get_for_update_member(g.current_user, workspace_id)
    Invitations.revoke(token)

    return redirect(url_for("workspaces.workspace_members", workspace_id=workspace.id))


@workspaces_bp.route(
    "/workspaces/<workspace_id>/invitations/<token>/resend", methods=["POST"]
)
def resend_invitation(workspace_id, token):
    invite = Invitations.resend(g.current_user, workspace_id, token)
    send_invite_email(g.current_user.full_name, invite.token, invite.email)
    flash("resent_workspace_invitation", {"user_name": invite.user_name})
    return redirect(url_for("workspaces.workspace_members", workspace_id=workspace_id))
