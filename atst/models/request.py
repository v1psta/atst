from sqlalchemy import Column, func, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import pendulum

from atst.models import Base
from atst.models.types import Id
from atst.models.request_status_event import RequestStatus
from atst.utils import first_or_none


class Request(Base):
    __tablename__ = "requests"

    id = Id()
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    body = Column(JSONB)
    status_events = relationship(
        "RequestStatusEvent", backref="request", order_by="RequestStatusEvent.sequence"
    )

    workspace = relationship("Workspace", uselist=False, backref="request")

    user_id = Column(ForeignKey("users.id"), nullable=False)
    creator = relationship("User")

    task_order_id = Column(ForeignKey("task_order.id"))
    task_order = relationship("TaskOrder")

    @property
    def status(self):
        return self.status_events[-1].new_status

    @property
    def status_displayname(self):
        return self.status_events[-1].displayname

    @property
    def annual_spend(self):
        monthly = self.body.get("details_of_use", {}).get("estimated_monthly_spend", 0)
        return monthly * 12

    @property
    def financial_verification(self):
        return self.body.get("financial_verification")

    @property
    def is_financially_verified(self):
        if self.task_order:
            return self.task_order.verified
        return False

    @property
    def last_submission_timestamp(self):
        def _is_submission(status_event):
            return status_event.new_status == RequestStatus.SUBMITTED

        last_submission = first_or_none(_is_submission, reversed(self.status_events))
        if last_submission:
            return pendulum.instance(last_submission.time_created)
        return None
