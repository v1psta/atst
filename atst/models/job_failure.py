from sqlalchemy import Column, ForeignKey

from atst.models import Base
from atst.models import mixins


class EnvironmentJobFailure(Base, mixins.JobFailureMixin):
    __tablename__ = "environment_job_failures"

    environment_id = Column(ForeignKey("environments.id"), nullable=False)


class EnvironmentRoleJobFailure(Base, mixins.JobFailureMixin):
    __tablename__ = "environment_role_job_failures"

    environment_role_id = Column(ForeignKey("environment_roles.id"), nullable=False)
