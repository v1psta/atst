from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.domain.exceptions import NotFoundError, UnauthorizedError
from atst.models.workspace import Workspace
from atst.models.workspace_role import WorkspaceRole
from atst.models.project import Project
from atst.domain.roles import Roles
from atst.domain.authz import Authorization


class WorkspacesQuery(object):
    # will a request have a TO association?
    # do we automatically create an entry for the request.creator in the
    # workspace_roles table?

    @classmethod
    def save(cls, *args):
        for arg in args:
            db.session.add(arg)
        db.session.commit()

    @classmethod
    def get(cls, workspace_id):
        try:
            workspace = db.session.query(Workspace).filter_by(id=workspace_id).one()
        except NoResultFound:
            raise NotFoundError("workspace")

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


class Workspaces(object):
    # will a request have a TO association?
    # do we automatically create an entry for the request.creator in the
    # workspace_roles table?

    @classmethod
    def create(cls, request, name=None):
        name = name or request.id
        workspace = Workspace(request=request, name=name)

        role = Roles.get("owner")
        workspace_role = WorkspaceRole(
            user=request.creator, role=role, workspace=workspace
        )

        WorkspacesQuery.save(workspace, workspace_role)

        return workspace

    @classmethod
    def get(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        if not Authorization.user_in_workspace(user, workspace):
            raise UnauthorizedError(user, "view workspace projects")
        return workspace

    @classmethod
    def get_by_request(cls, request):
        return WorkspacesQuery.get_by_request(request)

    @classmethod
    def get_many(cls, user):
        return WorkspacesQuery.get_many(user)


class ProjectsQuery(object):
    @classmethod
    def get(cls, workspace_id, project_id):
        try:
            project = (
                db.session.query(Project)
                .filter(Project.id == project_id, Workspace.id == workspace_id)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("project")

        return project


class Projects(object):
    @classmethod
    def get_for_edit(cls, user, workspace_id, project_id):
        project = ProjectsQuery.get(workspace_id, project_id)
        if not Authorization.has_workspace_permission(
            user, workspace, Permissions.VIEW_PROJECT_IN_WORKSPACE
        ):
            raise UnauthorizedError(user, "edit project")

        return project
