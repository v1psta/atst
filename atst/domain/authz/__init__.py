from atst.utils import first_or_none
from atst.models.permissions import Permissions
from atst.domain.exceptions import UnauthorizedError


class Authorization(object):
    @classmethod
    def has_portfolio_permission(cls, user, portfolio, permission):
        port_role = first_or_none(
            lambda pr: pr.portfolio == portfolio, user.portfolio_roles
        )
        if port_role:
            return permission in port_role.permissions
        else:
            return False

    @classmethod
    def has_atat_permission(cls, user, permission):
        return permission in user.permissions

    @classmethod
    def check_portfolio_permission(cls, user, portfolio, permission, message):
        if not (
            Authorization.has_atat_permission(user, permission)
            or Authorization.has_portfolio_permission(user, portfolio, permission)
        ):
            raise UnauthorizedError(user, message)

        return True

    @classmethod
    def check_atat_permission(cls, user, permission, message):
        if not Authorization.has_atat_permission(user, permission):
            raise UnauthorizedError(user, message)

        return True

    @classmethod
    def is_ko(cls, user, task_order):
        return user == task_order.contracting_officer

    @classmethod
    def is_cor(cls, user, task_order):
        return user == task_order.contracting_officer_representative

    @classmethod
    def is_so(cls, user, task_order):
        return user == task_order.security_officer

    @classmethod
    def check_is_ko_or_cor(cls, user, task_order):
        if Authorization.is_ko(user, task_order) or Authorization.is_cor(
            user, task_order
        ):
            return True
        else:
            raise UnauthorizedError(user, "not KO or COR")

    @classmethod
    def check_is_ko(cls, user, task_order):
        if task_order.contracting_officer != user:
            message = "review task order {}".format(task_order.id)
            raise UnauthorizedError(user, message)

    @classmethod
    def check_is_so(cls, user, task_order):
        if task_order.security_officer != user:
            message = "review task order {}".format(task_order.id)
            raise UnauthorizedError(user, message)


def user_can_access(user, permission, portfolio=None, message=None):
    if portfolio:
        Authorization.check_portfolio_permission(user, portfolio, permission, message)
    else:
        Authorization.check_atat_permission(user, permission, message)

    return True
