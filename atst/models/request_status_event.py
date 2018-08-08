from enum import Enum
from sqlalchemy import Column, func, ForeignKey, Enum as SQLAEnum
from sqlalchemy.types import DateTime, BigInteger
from sqlalchemy.schema import Sequence
from sqlalchemy.dialects.postgresql import UUID

from atst.models import Base
from atst.models.types import Id


class RequestStatus(Enum):
    STARTED = "started"
    PENDING_FINANCIAL_VERIFICATION = "pending_financial_verification"
    PENDING_CCPO_APPROVAL = "pending_ccpo_approval"
    APPROVED = "approved"


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
