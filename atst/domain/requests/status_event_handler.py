from flask import render_template

from atst.models.request_status_event import RequestStatus


class RequestStatusEventHandler(object):
    STATUS_TRANSITIONS = set([
        (
            RequestStatus.PENDING_CCPO_ACCEPTANCE,
            RequestStatus.PENDING_FINANCIAL_VERIFICATION,
        ),
        (
            RequestStatus.PENDING_CCPO_ACCEPTANCE,
            RequestStatus.CHANGES_REQUESTED,
        ),
        (
            RequestStatus.PENDING_CCPO_APPROVAL,
            RequestStatus.CHANGES_REQUESTED_TO_FINVER,
        ),
        (
            RequestStatus.PENDING_CCPO_APPROVAL,
            RequestStatus.APPROVED,
        ),
    ])

    def __init__(self, queue):
        self.queue = queue

    def handle_status_change(self, request, old_status, new_status):
        if (old_status, new_status) in self.STATUS_TRANSITIONS:
            self._send_email(request)

    def _send_email(self, request):
        email_body = render_template(
            "emails/request_status_change.txt", request=request
        )
        self.queue.send_mail(
            [request.creator.email], "Your JEDI request status has changed", email_body
        )
