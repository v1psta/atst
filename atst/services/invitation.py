from flask import render_template

from atst.domain.invitations import PortfolioInvitations, ApplicationInvitations
from atst.queue import queue
from atst.domain.task_orders import TaskOrders
from atst.domain.portfolio_roles import PortfolioRoles
from atst.models import ApplicationRole, PortfolioRole

OFFICER_INVITATIONS = {
    "ko_invite": {
        "role": "contracting_officer",
        "subject": "Review a task order",
        "template": "emails/portfolio/invitation.txt",
    },
    "cor_invite": {
        "role": "contracting_officer_representative",
        "subject": "Help with a task order",
        "template": "emails/portfolio/invitation.txt",
    },
    "so_invite": {
        "role": "security_officer",
        "subject": "Review security for a task order",
        "template": "emails/portfolio/invitation.txt",
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
    def __init__(self, inviter, member, email, subject="", email_template=None):
        self.inviter = inviter
        self.member = member
        self.email = email
        self.subject = subject
        self.email_template = email_template

        if isinstance(member, PortfolioRole):
            self.email_template = (
                self.email_template or "emails/portfolio/invitation.txt"
            )
            self.subject = (
                self.subject or "{} has invited you to a JEDI cloud portfolio"
            )
            self.domain_class = PortfolioInvitations
        elif isinstance(member, ApplicationRole):
            self.email_template = (
                self.email_template or "emails/application/invitation.txt"
            )
            self.subject = (
                self.subject or "{} has invited you to a JEDI cloud application"
            )
            self.domain_class = ApplicationInvitations

    def invite(self):
        invite = self._create_invite()
        self._send_invite_email(invite.token)

        return invite

    def _create_invite(self):
        user = self.member.user
        return self.domain_class.create(
            self.inviter,
            self.member,
            {"email": self.email, "dod_id": user.dod_id},
            commit=True,
        )

    def _send_invite_email(self, token):
        body = render_template(
            self.email_template, owner=self.inviter.full_name, token=token
        )
        queue.send_mail([self.email], self.subject.format(self.inviter.full_name), body)
