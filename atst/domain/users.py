from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from atst.database import db
from atst.models import User

from .roles import Roles
from .exceptions import NotFoundError, AlreadyExistsError, UnauthorizedError


class Users(object):
    @classmethod
    def get(cls, user_id):
        try:
            user = db.session.query(User).filter_by(id=user_id).one()
        except NoResultFound:
            raise NotFoundError("user")

        return user

    @classmethod
    def get_by_dod_id(cls, dod_id):
        try:
            user = db.session.query(User).filter_by(dod_id=dod_id).one()
        except NoResultFound:
            raise NotFoundError("user")

        return user

    @classmethod
    def create(cls, dod_id, atat_role_name=None, **kwargs):
        atat_role = Roles.get(atat_role_name)

        try:
            user = User(dod_id=dod_id, atat_role=atat_role, **kwargs)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise AlreadyExistsError("user")

        return user

    @classmethod
    def get_or_create_by_dod_id(cls, dod_id, **kwargs):
        try:
            user = Users.get_by_dod_id(dod_id)
        except NotFoundError:
            user = Users.create(dod_id, **kwargs)
            db.session.add(user)
            db.session.commit()

        return user

    @classmethod
    def update_role(cls, user_id, atat_role_name):

        user = Users.get(user_id)
        atat_role = Roles.get(atat_role_name)
        user.atat_role = atat_role

        db.session.add(user)
        db.session.commit()

        return user

    _UPDATEABLE_ATTRS = {
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "service_branch",
        "citizenship",
        "designation",
        "date_latest_training",
    }

    @classmethod
    def update(cls, user, user_delta):
        if not set(user_delta.keys()).issubset(Users._UPDATEABLE_ATTRS):
            raise UnauthorizedError(user, "update DOD ID")

        for key, value in user_delta.items():
            setattr(user, key, value)

        db.session.add(user)
        db.session.commit()

        return user
