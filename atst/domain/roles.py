from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models import Role
from .exceptions import NotFoundError


class Roles(object):
    @classmethod
    def get(cls, role_name):
        try:
            role = db.session.query(Role).filter_by(name=role_name).one()
        except NoResultFound:
            raise NotFoundError("role")

        return role

    @classmethod
    def get_all(cls):
        return db.session.query(Role).all()
