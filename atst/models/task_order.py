from sqlalchemy import Column, Numeric, String, ForeignKey, Date
from sqlalchemy.types import ARRAY
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins


class TaskOrder(Base, mixins.TimestampsMixin):
    __tablename__ = "task_orders"

    id = types.Id()

    workspace_id = Column(ForeignKey("workspaces.id"))
    workspace = relationship("Workspace")

    user_id = Column(ForeignKey("users.id"))
    creator = relationship("User")

    scope = Column(String)  # Cloud Project Scope
    defense_component = Column(String)  # Department of Defense Component
    app_migration = Column(String)  # App Migration
    native_apps = Column(String)  # Native Apps
    complexity = Column(ARRAY(String))  # Project Complexity
    complexity_other = Column(String)
    dev_team = Column(ARRAY(String))  # Development Team
    dev_team_other = Column(String)
    team_experience = Column(String)  # Team Experience
    start_date = Column(Date)  # Period of Performance
    end_date = Column(Date)
    clin_01 = Column(Numeric(scale=2))
    clin_02 = Column(Numeric(scale=2))
    clin_03 = Column(Numeric(scale=2))
    clin_04 = Column(Numeric(scale=2))
    ko_first_name = Column(String)  # First Name
    ko_last_name = Column(String)  # Last Name
    ko_email = Column(String)  # Email
    ko_dod_id = Column(String)  # DOD ID
    cor_first_name = Column(String)  # First Name
    cor_last_name = Column(String)  # Last Name
    cor_email = Column(String)  # Email
    cor_dod_id = Column(String)  # DOD ID
    so_first_name = Column(String)  # First Name
    so_last_name = Column(String)  # Last Name
    so_email = Column(String)  # Email
    so_dod_id = Column(String)  # DOD ID
    number = Column(String, unique=True)  # Task Order Number
    loa = Column(ARRAY(String))  # Line of Accounting (LOA)

    @property
    def budget(self):
        return sum(
            filter(None, [self.clin_01, self.clin_02, self.clin_03, self.clin_04])
        )

    def __repr__(self):
        return "<TaskOrder(number='{}', budget='{}', end_date='{}', id='{}')>".format(
            self.number, self.budget, self.end_date, self.id
        )

    def to_dictionary(self):
        return {
            "portfolio_name": self.workspace.name,
            **{
                c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name not in ["id"]
            },
        }
