from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.applications import Applications
from atst.domain.environments import Environments


class ScopedResource(object):
    """
    An abstract class that represents a resource that is restricted
    in some way by the priveleges of the user viewing that resource.
    """

    def __init__(self, user, resource):
        self.user = user
        self.resource = resource

    def __getattr__(self, name):
        return getattr(self.resource, name)

    def __eq__(self, other):
        return self.resource == other


class ScopedPortfolio(ScopedResource):
    """
    An object that obeys the same API as a Portfolio, but with the added
    functionality that it only returns sub-resources (applications and environments)
    that the given user is allowed to see.
    """

    @property
    def applications(self):
        can_view_all_applications = Authorization.has_portfolio_permission(
            self.user, self.resource, Permissions.VIEW_APPLICATION_IN_WORKSPACE
        )

        if can_view_all_applications:
            applications = self.resource.applications
        else:
            applications = Applications.for_user(self.user, self.resource)

        return [
            ScopedApplication(self.user, application) for application in applications
        ]


class ScopedApplication(ScopedResource):
    """
    An object that obeys the same API as a Portfolio, but with the added
    functionality that it only returns sub-resources (environments)
    that the given user is allowed to see.
    """

    @property
    def environments(self):
        can_view_all_environments = Authorization.has_portfolio_permission(
            self.user,
            self.resource.portfolio,
            Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
        )

        if can_view_all_environments:
            environments = self.resource.environments
        else:
            environments = Environments.for_user(self.user, self.resource)

        return environments
