from flask import render_template

from atst.domain.invitations import Invitations
from atst.queue import queue


class Invitation:
    def __init__(
        self,
        inviter,
        member,
        email,
        subject="{} has invited you to a JEDI Cloud Workspace",
        email_template="emails/invitation.txt",
    ):
        self.inviter = inviter
        self.member = member
        self.email = email
        self.subject = subject
        self.email_template = email_template

    def invite(self):
        invite = self._create_invite()
        self._send_invite_email(invite.token)

        return invite

    def _create_invite(self):
        return Invitations.create(self.inviter, self.member, self.email)

    def _send_invite_email(self, token):
        body = render_template(
            self.email_template, owner=self.inviter.full_name, token=token
        )
        queue.send_mail([self.email], self.subject.format(self.inviter.full_name), body)
