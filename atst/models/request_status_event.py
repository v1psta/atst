from enum import Enum
from sqlalchemy import Column, func, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime, BigInteger
from sqlalchemy.schema import Sequence
from sqlalchemy.dialects.postgresql import UUID

from atst.models import Base
from atst.models.types import Id


class RequestStatus(Enum):
    STARTED = "Started"
    SUBMITTED = "Submitted"
    PENDING_FINANCIAL_VERIFICATION = "Pending Financial Verification"
    PENDING_CCPO_ACCEPTANCE = "Pending CCPO Acceptance"
    PENDING_CCPO_APPROVAL = "Pending CCPO Approval"
    CHANGES_REQUESTED = "Changes Requested"
    CHANGES_REQUESTED_TO_FINVER = "Change Requested to Financial Verification"
    APPROVED = "Approved"
    EXPIRED = "Expired"
    DELETED = "Deleted"


class RequestStatusEvent(Base):
    __tablename__ = "request_status_events"

    id = Id()
    new_status = Column(SQLAEnum(RequestStatus))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    request_id = Column(
        UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE")
    )
    sequence = Column(
        BigInteger, Sequence("request_status_events_sequence_seq"), nullable=False
    )
    request_revision_id = Column(ForeignKey("request_revisions.id"), nullable=False)
    revision = relationship("RequestRevision")

    request_review_id = Column(ForeignKey("request_reviews.id"), nullable=True)
    review = relationship("RequestReview", back_populates="status")

    @property
    def displayname(self):
        return self.new_status.value
