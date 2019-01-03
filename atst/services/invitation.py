# send invite to KO
# create KO user (Workspaces.create_member)
#   needs workspace role name
# new_member = Workspaces.create_member(user, workspace, ws_role_name)
# invite = Invitations.create(user, new_member, form.data["email"])
# send_invite_email(g.current_user.full_name, invite.token, invite.email)
from flask import render_template

from atst.domain.workspaces import Workspaces
from atst.domain.invitations import Invitations
from atst.queue import queue


class Invitation:
    def __init__(
        self,
        inviter,
        workspace,
        user_info,
        subject="{} has invited you to a JEDI Cloud Workspace",
        email_template="emails/invitation.txt",
    ):
        self.inviter = inviter
        self.workspace = workspace
        self.user_info = user_info
        self.subject = subject
        self.email_template = email_template

    def invite(self):
        member = self._create_member()
        email = self.user_info.get("email")
        invite = self._create_invite(member, email)
        self._send_invite_email(invite.token, email)

        return invite

    def _create_member(self):
        return Workspaces.create_member(self.inviter, self.workspace, self.user_info)

    def _create_invite(self, member, email):
        return Invitations.create(self.inviter, member, email)

    def _send_invite_email(self, token, email):
        body = render_template(self.email_template, owner=self.inviter, token=token)
        queue.send_mail([email], self.subject.format(self.inviter), body)
