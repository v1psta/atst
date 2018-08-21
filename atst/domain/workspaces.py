from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.workspace import Workspace
from atst.models.workspace_role import WorkspaceRole
from atst.models.project import Project
from atst.models.environment import Environment
from atst.domain.exceptions import NotFoundError, UnauthorizedError
from atst.domain.roles import Roles


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

        db.session.add(workspace)
        db.session.add(workspace_role)
        db.session.commit()

        return workspace

    @classmethod
    def get(cls, user, workspace_id):
        try:
            workspace = db.session.query(Workspace).filter_by(id=workspace_id).one()
        except NoResultFound:
            raise NotFoundError("workspace")

        if user not in workspace.users:
            raise UnauthorizedError(user, "get workspace")

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


class Projects(object):
    @classmethod
    def create(cls, workspace, name, description):
        project = Project(workspace=workspace, name=name, description=description)

        db.session.add(project)
        db.session.commit()

        return project


class Environments(object):
    @classmethod
    def create(cls, project, name):
        environment = Environment(project=project, name=name)
        db.session.add(environment)
        db.session.commit()
        return environment


class Members(object):
    def __init__(self):
        pass

    @classmethod
    def create(cls, creator_id, body):
        pass

    @classmethod
    def get(cls, request_id):
        pass

    @classmethod
    def get_many(cls, workspace_id):
        return [
            {
                "first_name": "Danny",
                "last_name": "Knight",
                "email": "dknight@thenavy.mil",
                "dod_id": "1257892124",
                "workspace_role": "Developer",
                "status": "Pending",
                "num_projects": "4",
            },
            {
                "first_name": "Mario",
                "last_name": "Hudson",
                "email": "mhudson@thearmy.mil",
                "dod_id": "4357892125",
                "workspace_role": "CCPO",
                "status": "Active",
                "num_projects": "0",
            },
            {
                "first_name": "Louise",
                "last_name": "Greer",
                "email": "lgreer@theairforce.mil",
                "dod_id": "7257892125",
                "workspace_role": "Admin",
                "status": "Pending",
                "num_projects": "43",
            },
        ]

    @classmethod
    def update(cls, request_id, request_delta):
        pass
