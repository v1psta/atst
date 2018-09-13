from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound

from atst.domain.exceptions import NotFoundError
from atst.database import db


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
        except (NoResultFound, DataError):
            raise NotFoundError(cls.resource_name)

    @classmethod
    def get_all(cls):
        return db.session.query(cls.model).all()

    @classmethod
    def add_and_commit(cls, resource):
        db.session.add(resource)
        db.session.commit()
        return resource
