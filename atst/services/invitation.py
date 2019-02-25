from flask import render_template

from atst.domain.invitations import Invitations
from atst.queue import queue
from atst.domain.task_orders import TaskOrders
from atst.domain.portfolio_roles import PortfolioRoles

OFFICER_INVITATIONS = [
    {
        "field": "ko_invite",
        "role": "contracting_officer",
        "subject": "Review a task order",
        "template": "emails/invitation.txt",
    },
    {
        "field": "cor_invite",
        "role": "contracting_officer_representative",
        "subject": "Help with a task order",
        "template": "emails/invitation.txt",
    },
    {
        "field": "so_invite",
        "role": "security_officer",
        "subject": "Review security for a task order",
        "template": "emails/invitation.txt",
    },
]


def update_officer_invitations(user, task_order):
    for officer_type in OFFICER_INVITATIONS:
        field = officer_type["field"]
        if getattr(task_order, field) and not getattr(task_order, officer_type["role"]):
            officer_data = task_order.officer_dictionary(officer_type["role"])
            officer = TaskOrders.add_officer(
                user, task_order, officer_type["role"], officer_data
            )
            pf_officer_member = PortfolioRoles.get(task_order.portfolio.id, officer.id)
            invite_service = Invitation(
                user,
                pf_officer_member,
                officer_data["email"],
                subject=officer_type["subject"],
                email_template=officer_type["template"],
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
