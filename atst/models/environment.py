from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from atst.models import Base
from atst.models.types import Id
from atst.models import mixins


class Environment(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin
):
    __tablename__ = "environments"

    id = Id()
    name = Column(String, nullable=False)

    application_id = Column(ForeignKey("applications.id"), nullable=False)
    application = relationship("Application")

    # User user.id as the foreign key here beacuse the Environment creator may
    # not have an application role. We may need to revisit this if we receive any
    # requirements around tracking an environment's custodian.
    creator_id = Column(ForeignKey("users.id"), nullable=False)
    creator = relationship("User")

    cloud_id = Column(String)
    root_user_info = Column(JSONB)
    baseline_info = Column(JSONB)

    job_failures = relationship("EnvironmentJobFailure")

    @property
    def users(self):
        return {r.application_role.user for r in self.roles}

    @property
    def num_users(self):
        return len(self.users)

    @property
    def displayname(self):
        return self.name

    @property
    def portfolio(self):
        return self.application.portfolio

    @property
    def portfolio_id(self):
        return self.application.portfolio_id

    def __repr__(self):
        return "<Environment(name='{}', num_users='{}', application='{}', portfolio='{}', id='{}')>".format(
            self.name,
            self.num_users,
            self.application.name,
            self.application.portfolio.name,
            self.id,
        )

    @property
    def history(self):
        return self.get_changes()
