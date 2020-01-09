from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from atst.database import db
from atst.models import User

from .permission_sets import PermissionSets
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
    def get_ccpo_users(cls):
        return (
            db.session.query(User)
            .filter(User.permission_sets != None)
            .order_by(User.last_name)
            .all()
        )

    @classmethod
    def create(cls, dod_id, permission_sets=None, **kwargs):
        if permission_sets:
            permission_sets = PermissionSets.get_many(permission_sets)
        else:
            permission_sets = []

        try:
            user = User(dod_id=dod_id, permission_sets=permission_sets, **kwargs)
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

    _UPDATEABLE_ATTRS = {
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "phone_ext",
        "service_branch",
        "citizenship",
        "designation",
        "date_latest_training",
    }

    @classmethod
    def update(cls, user, user_delta):
        delta_set = set(user_delta.keys())
        if not set(delta_set).issubset(Users._UPDATEABLE_ATTRS):
            unpermitted = delta_set - Users._UPDATEABLE_ATTRS
            raise UnauthorizedError(user, "update {}".format(", ".join(unpermitted)))

        for key, value in user_delta.items():
            setattr(user, key, value)

        db.session.add(user)
        db.session.commit()

        return user

    @classmethod
    def give_ccpo_perms(cls, user):
        user.permission_sets = PermissionSets.get_all()
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def revoke_ccpo_perms(cls, user):
        user.permission_sets = []
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def update_last_login(cls, user):
        user.last_login = datetime.now()
        db.session.add(user)
        db.session.commit()

    @classmethod
    def update_last_session_id(cls, user, session_id):
        user.last_session_id = session_id
        db.session.add(user)
        db.session.commit()
