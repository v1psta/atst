import datetime
from enum import Enum
import secrets

from sqlalchemy import Column, ForeignKey, Enum as SQLAEnum, TIMESTAMP, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from atst.models import Base, types
from atst.models.mixins.timestamps import TimestampsMixin
from atst.models.mixins.auditable import AuditableMixin


class Status(Enum):
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    PENDING = "pending"
    REJECTED_WRONG_USER = "rejected_wrong_user"
    REJECTED_EXPIRED = "rejected_expired"


class Invitation(Base, TimestampsMixin, AuditableMixin):
    __tablename__ = "invitations"

    id = types.Id()

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user = relationship("User", backref="invitations", foreign_keys=[user_id])

    workspace_role_id = Column(
        UUID(as_uuid=True), ForeignKey("workspace_roles.id"), index=True
    )
    workspace_role = relationship(
        "WorkspaceRole",
        backref=backref("invitations", order_by="Invitation.time_created"),
    )

    inviter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    inviter = relationship("User", backref="sent_invites", foreign_keys=[inviter_id])

    status = Column(SQLAEnum(Status, native_enum=False, default=Status.PENDING))

    expiration_time = Column(TIMESTAMP(timezone=True))

    token = Column(String, index=True, default=lambda: secrets.token_urlsafe())

    email = Column(String, nullable=False)

    def __repr__(self):
        return "<Invitation(user='{}', workspace_role='{}', id='{}', email='{}')>".format(
            self.user_id, self.workspace_role_id, self.id, self.email
        )

    @property
    def is_accepted(self):
        return self.status == Status.ACCEPTED

    @property
    def is_revoked(self):
        return self.status == Status.REVOKED

    @property
    def is_pending(self):
        return self.status == Status.PENDING

    @property
    def is_rejected(self):
        return self.status in [Status.REJECTED_WRONG_USER, Status.REJECTED_EXPIRED]

    @property
    def is_rejected_expired(self):
        return self.status == Status.REJECTED_EXPIRED

    @property
    def is_rejected_wrong_user(self):
        return self.status == Status.REJECTED_WRONG_USER

    @property
    def is_expired(self):
        return (
            datetime.datetime.now(self.expiration_time.tzinfo) > self.expiration_time
            and not self.status == Status.ACCEPTED
        )

    @property
    def is_inactive(self):
        return self.is_expired or self.status in [
            Status.REJECTED_WRONG_USER,
            Status.REJECTED_EXPIRED,
            Status.REVOKED,
        ]

    @property
    def workspace(self):
        if self.workspace_role:
            return self.workspace_role.workspace

    @property
    def user_name(self):
        return self.workspace_role.user.full_name

    @property
    def is_revokable(self):
        return self.is_pending and not self.is_expired

    @property
    def user_dod_id(self):
        return self.user.dod_id if self.user is not None else None

    @property
    def event_details(self):
        return {"email": self.email, "dod_id": self.user_dod_id}

    @property
    def history(self):
        changes = self.get_changes()
        change_set = {}

        if "status" in changes:
            change_set["status"] = [s.name for s in changes["status"]]

        return change_set

    @property
    def workspace_id(self):
        return self.workspace_role.workspace_id
