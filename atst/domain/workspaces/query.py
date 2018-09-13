from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.domain.exceptions import NotFoundError
from atst.models.workspace import Workspace
from atst.models.workspace_role import WorkspaceRole


class Query(object):

    model = None

    @property
    def resource_name(cls):
        return cls.model.__class__.lower()

    @classmethod
    def create(cls, **kwargs):
        # pylint: disable=E1102
        return cls.model(**kwargs)

    @classmethod
    def get(cls, id_):
        try:
            resource = db.session.query(cls.model).filter_by(id=id_).one()
            return resource
        except NoResultFound:
            raise NotFoundError(cls.resource_name)

    @classmethod
    def get_all(cls):
        return db.session.query(cls.model).all()

    @classmethod
    def add_and_commit(cls, resource):
        db.session.add(resource)
        db.session.commit()
        return resource


class WorkspaceQuery(Query):
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
            .all()
        )

    @classmethod
    def create_workspace_role(cls, user, role, workspace):
        return WorkspaceRole(user=user, role=role, workspace=workspace)
