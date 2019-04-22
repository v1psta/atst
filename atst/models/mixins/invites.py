import datetime
from enum import Enum
import secrets

from sqlalchemy import Column, ForeignKey, Enum as SQLAEnum, TIMESTAMP, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import types


class Status(Enum):
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    PENDING = "pending"
    REJECTED_WRONG_USER = "rejected_wrong_user"
    REJECTED_EXPIRED = "rejected_expired"


class InvitesMixin(object):
    id = types.Id()

    @declared_attr
    def user_id(cls):
        return Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    @declared_attr
    def user(cls):
        return relationship("User", foreign_keys=[cls.user_id])

    @declared_attr
    def inviter_id(cls):
        return Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    @declared_attr
    def inviter(cls):
        return relationship("User", foreign_keys=[cls.inviter_id])

    status = Column(SQLAEnum(Status, native_enum=False, default=Status.PENDING))

    expiration_time = Column(TIMESTAMP(timezone=True))

    token = Column(String, index=True, default=lambda: secrets.token_urlsafe())

    email = Column(String, nullable=False)

    def __repr__(self):
        role_id = self.role.id if self.role else None
        return "<{}(user='{}', role='{}', id='{}', email='{}')>".format(
            self.__class__.__name__, self.user_id, role_id, self.id, self.email
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
    def user_name(self):
        return self.role.user.full_name

    @property
    def is_revokable(self):
        return self.is_pending and not self.is_expired

    @property
    def can_resend(self):
        return self.is_pending or self.is_expired

    @property
    def user_dod_id(self):
        return self.user.dod_id if self.user is not None else None
