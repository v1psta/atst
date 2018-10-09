from atst.models.permissions import Permissions
from atst.domain.authz import Authorization
from atst.domain.exceptions import UnauthorizedError


class RequestsAuthorization(object):
    def __init__(self, user, request):
        self.user = user
        self.request = request

    @property
    def can_view(self):
        return (
            Authorization.has_atat_permission(
                self.user, Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST
            )
            or self.request.creator == self.user
        )

    def check_can_view(self, message):
        if not self.can_view:
            raise UnauthorizedError(self.user, message)

    def check_can_approve(self):
        return Authorization.check_atat_permission(
            self.user,
            Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST,
            "cannot review and approve requests",
        )
