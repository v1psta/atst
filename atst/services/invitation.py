from flask import render_template

from atst.domain.invitations import Invitations
from atst.queue import queue
from atst.domain.task_orders import TaskOrders
from atst.domain.portfolio_roles import PortfolioRoles

OFFICER_INVITATIONS = {
    "ko_invite": {
        "role": "contracting_officer",
        "subject": "Review a task order",
        "template": "emails/invitation.txt",
    },
    "cor_invite": {
        "role": "contracting_officer_representative",
        "subject": "Help with a task order",
        "template": "emails/invitation.txt",
    },
    "so_invite": {
        "role": "security_officer",
        "subject": "Review security for a task order",
        "template": "emails/invitation.txt",
    },
}


def update_officer_invitations(user, task_order):
    for invite_type in dict.keys(OFFICER_INVITATIONS):
        invite_opts = OFFICER_INVITATIONS[invite_type]

        if getattr(task_order, invite_type) and not getattr(
            task_order, invite_opts["role"]
        ):
            officer_data = task_order.officer_dictionary(invite_opts["role"])
            officer = TaskOrders.add_officer(
                task_order, invite_opts["role"], officer_data
            )
            pf_officer_member = PortfolioRoles.get(task_order.portfolio.id, officer.id)
            invite_service = Invitation(
                user,
                pf_officer_member,
                officer_data["email"],
                subject=invite_opts["subject"],
                email_template=invite_opts["template"],
            )
            invite_service.invite()


class Invitation:
    def __init__(
        self,
        inviter,
        member,
        email,
        subject="{} has invited you to a JEDI Cloud Portfolio",
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
