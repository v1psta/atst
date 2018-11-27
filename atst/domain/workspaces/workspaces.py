from atst.domain.roles import Roles
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.users import Users
from atst.domain.workspace_roles import WorkspaceRoles
from atst.domain.environments import Environments
from atst.models.workspace_role import Status as WorkspaceRoleStatus

from .query import WorkspacesQuery
from .scopes import ScopedWorkspace


class WorkspaceError(Exception):
    pass


class Workspaces(object):
    @classmethod
    def create(cls, request, name=None):
        name = name or request.displayname
        workspace = WorkspacesQuery.create(request=request, name=name)
        Workspaces._create_workspace_role(
            request.creator, workspace, "owner", status=WorkspaceRoleStatus.ACTIVE
        )
        WorkspacesQuery.add_and_commit(workspace)
        return workspace

    @classmethod
    def get(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user, workspace, Permissions.VIEW_WORKSPACE, "get workspace"
        )

        return ScopedWorkspace(user, workspace)

    @classmethod
    def get_for_update_projects(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user, workspace, Permissions.ADD_APPLICATION_IN_WORKSPACE, "add project"
        )

        return workspace

    @classmethod
    def get_for_update_information(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.EDIT_WORKSPACE_INFORMATION,
            "update workspace information",
        )

        return workspace

    @classmethod
    def get_for_update_member(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            "update a workspace member",
        )

        return workspace

    @classmethod
    def get_by_request(cls, request):
        return WorkspacesQuery.get_by_request(request)

    @classmethod
    def get_with_members(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.VIEW_WORKSPACE_MEMBERS,
            "view workspace members",
        )

        return workspace

    @classmethod
    def for_user(cls, user):
        if Authorization.has_atat_permission(user, Permissions.VIEW_WORKSPACE):
            workspaces = WorkspacesQuery.get_all()
        else:
            workspaces = WorkspacesQuery.get_for_user(user)
        return workspaces

    @classmethod
    def create_member(cls, user, workspace, data):
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            "create workspace member",
        )

        new_user = Users.get_or_create_by_dod_id(
            data["dod_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            atat_role_name="default",
            provisional=True,
        )
        return Workspaces.add_member(workspace, new_user, data["workspace_role"])

    @classmethod
    def add_member(cls, workspace, member, role_name):
        workspace_role = WorkspaceRoles.add(member, workspace.id, role_name)
        return workspace_role

    @classmethod
    def update_member(cls, user, workspace, member, role_name):
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            "edit workspace member",
        )

        return WorkspaceRoles.update_role(member, role_name)

    @classmethod
    def _create_workspace_role(
        cls, user, workspace, role_name, status=WorkspaceRoleStatus.PENDING
    ):
        role = Roles.get(role_name)
        workspace_role = WorkspacesQuery.create_workspace_role(
            user, role, workspace, status=status
        )
        WorkspacesQuery.add_and_commit(workspace_role)
        return workspace_role

    @classmethod
    def update(cls, workspace, new_data):
        if "name" in new_data:
            workspace.name = new_data["name"]

        WorkspacesQuery.add_and_commit(workspace)

    @classmethod
    def can_revoke_access(cls, workspace, workspace_role):
        return workspace_role.user != workspace.owner

    @classmethod
    def revoke_access(cls, user, workspace_id, workspace_role_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            "revoke workspace access",
        )
        workspace_role = WorkspaceRoles.get_by_id(workspace_role_id)

        if not Workspaces.can_revoke_access(workspace, workspace_role):
            raise WorkspaceError("cannot revoke workspace access for this user")

        workspace_role.status = WorkspaceRoleStatus.DISABLED
        for environment in workspace.all_environments:
            # TODO: Implement Environments.revoke_access
            Environments.revoke_access(user, environment, workspace_role.user)
        WorkspacesQuery.add_and_commit(workspace_role)

        return workspace_role
