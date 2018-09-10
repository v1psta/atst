from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.projects import Projects
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


class ScopedWorkspace(ScopedResource):
    """
    An object that obeys the same API as a Workspace, but with the added
    functionality that it only returns sub-resources (projects and environments)
    that the given user is allowed to see.
    """

    @property
    def projects(self):
        can_view_all_projects = Authorization.has_workspace_permission(
            self.user, self.resource, Permissions.VIEW_APPLICATION_IN_WORKSPACE
        )

        if can_view_all_projects:
            projects = self.resource.projects
        else:
            projects = Projects.for_user(self.user, self.resource)

        return [ScopedProject(self.user, project) for project in projects]


class ScopedProject(ScopedResource):
    """
    An object that obeys the same API as a Workspace, but with the added
    functionality that it only returns sub-resources (environments)
    that the given user is allowed to see.
    """

    @property
    def environments(self):
        can_view_all_environments = Authorization.has_workspace_permission(
            self.user, self.resource, Permissions.VIEW_ENVIRONMENT_IN_APPLICATION
        )

        if can_view_all_environments:
            environments = self.resource.environments
        else:
            environments = Environments.for_user(self.user, self.resource)

        return environments
