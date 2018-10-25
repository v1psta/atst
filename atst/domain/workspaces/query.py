from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.domain.common import Query
from atst.domain.exceptions import NotFoundError
from atst.models.workspace import Workspace
from atst.models.workspace_role import WorkspaceRole


class WorkspacesQuery(Query):
    model = Workspace

    @classmethod
    def get_by_request(cls, request):
        try:
            workspace = db.session.query(Workspace).filter_by(request=request).one()
        except NoResultFound:
            raise NotFoundError("workspace")

        return workspace

    @classmethod
    def get_for_user(cls, user):
        return (
            db.session.query(Workspace)
            .join(WorkspaceRole)
            .filter(WorkspaceRole.user == user)
            .filter(WorkspaceRole.accepted == True)
            .all()
        )

    @classmethod
    def create_workspace_role(cls, user, role, workspace):
        return WorkspaceRole(user=user, role=role, workspace=workspace)

    @classmethod
    def get_role_for_workspace_and_user(cls, workspace, user):
        return (
            db.session.query(WorkspaceRole)
            .filter(WorkspaceRole.user == user)
            .filter(WorkspaceRole.workspace == workspace)
            .one()
        )
