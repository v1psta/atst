import datetime
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.invitation import Invitation, Status as InvitationStatus
from atst.domain.workspace_users import WorkspaceUsers

from .exceptions import NotFoundError


class WrongUserError(Exception):
    def __init__(self, user, invite):
        self.user = user
        self.invite = invite

    @property
    def message(self):
        return "User {} with DOD ID {} does not match expected DOD ID {} for invitation {}".format(self.user.id, self.user.dod_id, self.invite.user.dod_id, self.invite.id)

class InvitationError(Exception):
    def __init__(self, invite):
        self.invite = invite

    @property
    def message(self):
        return "{} has a status of {}".format(self.invite.id, self.invite.status.value)


class Invitations(object):
    # number of minutes a given invitation is considered valid
    EXPIRATION_LIMIT_MINUTES = 360

    @classmethod
    def _get(cls, token):
        try:
            invite = db.session.query(Invitation).filter_by(token=token).one()
        except NoResultFound:
            raise NotFoundError("invite")

        return invite

    @classmethod
    def create(cls, workspace_role, inviter, user):
        invite = Invitation(
            workspace_role=workspace_role,
            inviter=inviter,
            user=user,
            status=InvitationStatus.PENDING,
            expiration_time=Invitations.current_expiration_time(),
        )
        db.session.add(invite)
        db.session.commit()

        return invite

    @classmethod
    def accept(cls, user, token):
        invite = Invitations._get(token)

        if invite.user.dod_id != user.dod_id:
            raise WrongUserError(user, invite)

        if invite.is_expired:
            invite.status = InvitationStatus.REJECTED
        elif invite.is_pending:
            invite.status = InvitationStatus.ACCEPTED

        db.session.add(invite)
        db.session.commit()

        if invite.is_revoked or invite.is_rejected:
            raise InvitationError(invite)

        WorkspaceUsers.enable(invite.workspace_role)

        return invite

    @classmethod
    def current_expiration_time(cls):
        return datetime.datetime.now() + datetime.timedelta(
            minutes=Invitations.EXPIRATION_LIMIT_MINUTES
        )
