import datetime
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models import Invitation

from .exceptions import NotFoundError


class InvitationExpired(Exception):
    def __init__(self, invite_id):
        self.invite_id = invite_id

    @property
    def message(self):
        return "{} has expired".format(self.invite_id)


class Invitations(object):
    # number of minutes a given invitation is considered valid
    EXPIRATION_LIMIT_MINUTES = 360

    @classmethod
    def _get(cls, invite_id):
        try:
            invite = db.session.query(Invitation).filter_by(id=invite_id).one()
        except NoResultFound:
            raise NotFoundError("invite")

        return invite

    @classmethod
    def create(cls, workspace, inviter, user):
        invite = Invitation(workspace=workspace, inviter=inviter, user=user, valid=True)
        db.session.add(invite)
        db.session.commit()

        return invite

    @classmethod
    def accept(cls, invite_id):
        invite = Invitations._get(invite_id)
        valid = Invitations.is_valid(invite)

        invite.valid = False
        db.session.add(invite)
        db.session.commit()

        if not valid:
            raise InvitationExpired(invite_id)

        return invite

    @classmethod
    def is_valid(cls, invite):
        return invite.valid and not Invitations.is_expired(invite)

    @classmethod
    def is_expired(cls, invite):
        time_created = invite.time_created
        expiration = datetime.datetime.now(time_created.tzinfo) - datetime.timedelta(
            minutes=Invitations.EXPIRATION_LIMIT_MINUTES
        )
        return invite.time_created < expiration
