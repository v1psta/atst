from flask import render_template

from atst.models.request_status_event import RequestStatus


class RequestStatusEventHandler(object):
    def __init__(self, queue):
        self.queue = queue

    def handle_status_change(self, request, old_status, new_status):
        handler = self._get_handler(old_status, new_status)
        if handler:
            handler(request)

    def _get_handler(self, old_status, new_status):
        return {
            (
                RequestStatus.PENDING_CCPO_ACCEPTANCE,
                RequestStatus.PENDING_FINANCIAL_VERIFICATION,
            ): self._send_email,
            (
                RequestStatus.PENDING_CCPO_ACCEPTANCE,
                RequestStatus.CHANGES_REQUESTED,
            ): self._send_email,
            (
                RequestStatus.PENDING_CCPO_APPROVAL,
                RequestStatus.CHANGES_REQUESTED_TO_FINVER,
            ): self._send_email,
            (
                RequestStatus.PENDING_CCPO_APPROVAL,
                RequestStatus.APPROVED,
            ): self._send_email,
        }.get((old_status, new_status))

    def _send_email(self, request):
        email_body = render_template(
            "emails/request_status_change.txt", request=request
        )
        self.queue.send_mail(
            [request.creator.email], "Your JEDI request status has changed", email_body
        )
