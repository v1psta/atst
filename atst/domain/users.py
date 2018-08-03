from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from atst.database import db
from atst.models import User

from .roles import Roles
from .exceptions import NotFoundError, AlreadyExistsError


class Users(object):

    @classmethod
    def get(cls, user_id):
        try:
            user = db.session.query(User).filter_by(id=user_id).one()
        except NoResultFound:
            raise NotFoundError("user")

        return user

    @classmethod
    def create(cls, atat_role_name, **kwargs):
        atat_role = Roles.get(atat_role_name)

        try:
            user = User(atat_role=atat_role, **kwargs)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            raise AlreadyExistsError("user")

        return user

    @classmethod
    def get_or_create(cls, user_id, **kwargs):
        try:
            user = Users.get(user_id)
        except NotFoundError:
            user = Users.create(id=user_id, **kwargs)
            db.session.add(user)
            db.session.commit()

        return user

    @classmethod
    def update(cls, user_id, atat_role_name):

        user = Users.get(user_id)
        atat_role = Roles.get(atat_role_name)
        user.atat_role = atat_role

        db.session.add(user)
        db.session.commit()

        return user
