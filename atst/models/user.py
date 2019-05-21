from sqlalchemy import String, ForeignKey, Column, Date, Boolean, Table, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from atst.models import Base, types, mixins
from atst.models.permissions import Permissions
from atst.models.portfolio_invitation import PortfolioInvitation
from atst.models.application_invitation import ApplicationInvitation


users_permission_sets = Table(
    "users_permission_sets",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("permission_set_id", UUID(as_uuid=True), ForeignKey("permission_sets.id")),
)


class User(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.PermissionsMixin
):
    __tablename__ = "users"

    id = types.Id()
    username = Column(String)

    permission_sets = relationship("PermissionSet", secondary=users_permission_sets)

    portfolio_roles = relationship("PortfolioRole", backref="user")
    application_roles = relationship(
        "ApplicationRole",
        backref="user",
        primaryjoin="and_(ApplicationRole.user_id==User.id, ApplicationRole.deleted==False)",
    )

    portfolio_invitations = relationship(
        "PortfolioInvitation", foreign_keys=PortfolioInvitation.user_id
    )
    sent_portfolio_invitations = relationship(
        "PortfolioInvitation", foreign_keys=PortfolioInvitation.inviter_id
    )

    application_invitations = relationship(
        "ApplicationInvitation", foreign_keys=ApplicationInvitation.user_id
    )
    sent_application_invitations = relationship(
        "ApplicationInvitation", foreign_keys=ApplicationInvitation.inviter_id
    )

    email = Column(String)
    dod_id = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    phone_ext = Column(String)
    service_branch = Column(String)
    citizenship = Column(String)
    designation = Column(String)
    date_latest_training = Column(Date)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)

    provisional = Column(Boolean)

    cloud_id = Column(String)

    REQUIRED_FIELDS = [
        "email",
        "dod_id",
        "first_name",
        "last_name",
        "phone_number",
        "service_branch",
        "citizenship",
        "designation",
        "date_latest_training",
    ]

    @property
    def profile_complete(self):
        return all(
            [
                getattr(self, field_name) is not None
                for field_name in self.REQUIRED_FIELDS
            ]
        )

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def has_portfolios(self):
        return (Permissions.VIEW_PORTFOLIO in self.permissions) or self.portfolio_roles

    @property
    def displayname(self):
        return self.full_name

    @property
    def portfolio_id(self):
        return None

    @property
    def application_id(self):
        return None

    def __repr__(self):
        return "<User(name='{}', dod_id='{}', email='{}', has_portfolios='{}', id='{}')>".format(
            self.full_name, self.dod_id, self.email, self.has_portfolios, self.id
        )

    def to_dictionary(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["id"]
        }
