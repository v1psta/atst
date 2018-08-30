import pendulum
from sqlalchemy import Column, func, ForeignKey, String, Boolean, Integer, Date
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.mixins import TimestampsMixin
from atst.models.types import Id


class RequestRevision(Base, TimestampsMixin):
    __tablename__ = "request_revisions"

    id = Id()
    request_id = Column(ForeignKey("requests.id"), nullable=False)
    request = relationship("Request", back_populates="revisions")

    # primary_poc
    am_poc = Column(Boolean, default=False)
    dodid_poc = Column(String)
    email_poc = Column(String)
    fname_poc = Column(String)
    lname_poc = Column(String)

    # details_of_use
    jedi_usage = Column(String)
    start_date = Column(Date())
    cloud_native = Column(Boolean)
    dollar_value = Column(Integer)
    dod_component = Column(String)
    data_transfers = Column(String)
    expected_completion_date = Column(String)
    jedi_migration = Column(Boolean)
    num_software_systems = Column(Integer)
    number_user_sessions = Column(Integer)
    average_daily_traffic = Column(Integer)
    engineering_assessment = Column(Boolean)
    technical_support_team = Column(Boolean)
    estimated_monthly_spend = Column(Integer)
    average_daily_traffic_gb = Column(Integer)
    rationalization_software_systems = Column(Boolean)
    organization_providing_assistance = Column(String)

    # information_about_you
    citizenship = Column(String)
    designation = Column(String)
    phone_number = Column(String)
    email_request = Column(String)
    fname_request = Column(String)
    lname_request = Column(String)
    service_branch = Column(String)
    date_latest_training = Column(Date())

    # financial_verification
    pe_id = Column(String)
    task_order_number = Column(String)
    fname_co = Column(String)
    lname_co = Column(String)
    email_co = Column(String)
    office_co = Column(String)
    fname_cor = Column(String)
    lname_cor = Column(String)
    email_cor = Column(String)
    office_cor = Column(String)
    uii_ids = Column(String)
    treasury_code = Column(String)
    ba_code = Column(String)

    _BOOLS = ["am_poc", "jedi_migration", "engineering_assessment", "technical_support_team", "rationalization_software_systems", "cloud_native"]
    _TIMESTAMPS = ["start_date", "date_latest_training"]

    @classmethod
    def create_from_request_body(cls, request, **body):
        coerced_bools = {k: v == "yes" for k,v in body.items() if k in RequestRevision._BOOLS}
        coerced_timestamps = {k: pendulum.parse(v) for k,v in body.items() if k in RequestRevision._TIMESTAMPS}
        body = {**body, **coerced_bools, **coerced_timestamps}
        return RequestRevision(request=request, **body)
