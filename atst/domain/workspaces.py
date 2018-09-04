from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.workspace import Workspace
from atst.models.workspace_role import WorkspaceRole
from atst.domain.exceptions import NotFoundError, UnauthorizedError
from atst.domain.roles import Roles
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.users import Users
from atst.domain.workspace_users import WorkspaceUsers


class Workspaces(object):
    @classmethod
    def create(cls, request, name=None):
        name = name or request.id
        workspace = Workspace(request=request, name=name)
        Workspaces._create_workspace_role(request.creator, workspace, "owner")

        db.session.add(workspace)
        db.session.commit()

        return workspace

    @classmethod
    def get(cls, user, workspace_id):
        try:
            workspace = db.session.query(Workspace).filter_by(id=workspace_id).one()
        except NoResultFound:
            raise NotFoundError("workspace")

        if not Authorization.is_in_workspace(user, workspace):
            raise UnauthorizedError(user, "get workspace")

        return workspace

    @classmethod
    def get_for_update(cls, user, workspace_id):
        workspace = Workspaces.get(user, workspace_id)
        if not Authorization.has_workspace_permission(
            user, workspace, Permissions.ADD_APPLICATION_IN_WORKSPACE
        ):
            raise UnauthorizedError(user, "add project")
        return workspace

    @classmethod
    def get_by_request(cls, request):
        try:
            workspace = db.session.query(Workspace).filter_by(request=request).one()
        except NoResultFound:
            raise NotFoundError("workspace")

        return workspace

    @classmethod
    def get_many(cls, user):
        workspaces = (
            db.session.query(Workspace)
            .join(WorkspaceRole)
            .filter(WorkspaceRole.user == user)
            .all()
        )
        return workspaces

    @classmethod
    def create_member(cls, user, workspace, data):
        if not Authorization.has_workspace_permission(
            user, workspace, Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE
        ):
            raise UnauthorizedError(user, "create workspace member")

        new_user = Users.get_or_create_by_dod_id(
            data["dod_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
        )
        workspace_user = WorkspaceUsers.add(
            new_user, workspace.id, data["workspace_role"]
        )
        return workspace_user

    @classmethod
    def _create_workspace_role(cls, user, workspace, role_name):
        role = Roles.get(role_name)
        workspace_role = WorkspaceRole(user=user, role=role, workspace=workspace)
        db.session.add(workspace_role)
        return workspace_role
