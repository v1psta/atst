import datetime
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.invitation import Invitation, Status as InvitationStatus
from atst.domain.workspace_roles import WorkspaceRoles

from .exceptions import NotFoundError


class WrongUserError(Exception):
    def __init__(self, user, invite):
        self.user = user
        self.invite = invite

    @property
    def message(self):
        return "User {} with DOD ID {} does not match expected DOD ID {} for invitation {}".format(
            self.user.id, self.user.dod_id, self.invite.user.dod_id, self.invite.id
        )


class ExpiredError(Exception):
    def __init__(self, invite):
        self.invite = invite

    @property
    def message(self):
        return "Invitation {} has expired.".format(self.invite.id)


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
            if invite.is_pending:
                Invitations._update_status(invite, InvitationStatus.REJECTED_WRONG_USER)
            raise WrongUserError(user, invite)

        elif invite.is_expired:
            Invitations._update_status(invite, InvitationStatus.REJECTED_EXPIRED)
            raise ExpiredError(invite)

        elif invite.is_accepted or invite.is_revoked or invite.is_rejected:
            raise InvitationError(invite)

        elif invite.is_pending:
            Invitations._update_status(invite, InvitationStatus.ACCEPTED)
            WorkspaceRoles.enable(invite.workspace_role)
            return invite

    @classmethod
    def current_expiration_time(cls):
        return datetime.datetime.now() + datetime.timedelta(
            minutes=Invitations.EXPIRATION_LIMIT_MINUTES
        )

    @classmethod
    def _update_status(cls, invite, new_status):
        invite.status = new_status
        db.session.add(invite)
        db.session.commit()

        return invite

    @classmethod
    def revoke(cls, token):
        invite = Invitations._get(token)
        return Invitations._update_status(invite, InvitationStatus.REVOKED)
