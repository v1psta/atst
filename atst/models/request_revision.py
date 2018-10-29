from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Boolean,
    Integer,
    Date,
    BigInteger,
    Sequence,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from atst.models import Base
from atst.models import mixins
from atst.models.types import Id


class RequestRevision(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "request_revisions"

    id = Id()
    request_id = Column(ForeignKey("requests.id"), nullable=False)
    request = relationship("Request", back_populates="revisions")
    sequence = Column(
        BigInteger, Sequence("request_revisions_sequence_seq"), nullable=False
    )

    # primary_poc
    am_poc = Column(Boolean)
    dodid_poc = Column(String)
    email_poc = Column(String)
    fname_poc = Column(String)
    lname_poc = Column(String)

    # details_of_use
    jedi_usage = Column(String)
    start_date = Column(Date)
    cloud_native = Column(String)
    dollar_value = Column(Integer)
    dod_component = Column(String)
    data_transfers = Column(String)
    expected_completion_date = Column(String)
    jedi_migration = Column(String)
    num_software_systems = Column(Integer)
    number_user_sessions = Column(Integer)
    average_daily_traffic = Column(Integer)
    engineering_assessment = Column(String)
    technical_support_team = Column(String)
    estimated_monthly_spend = Column(Integer)
    average_daily_traffic_gb = Column(Integer)
    rationalization_software_systems = Column(String)
    organization_providing_assistance = Column(String)
    name = Column(String)

    # information_about_you
    citizenship = Column(String)
    designation = Column(String)
    phone_number = Column(String)
    phone_ext = Column(String)
    email_request = Column(String)
    fname_request = Column(String)
    lname_request = Column(String)
    service_branch = Column(String)
    date_latest_training = Column(Date)

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
    uii_ids = Column(ARRAY(String))
    treasury_code = Column(String)
    ba_code = Column(String)

    def __repr__(self):
        return "<RequestRevision(request='{}', id='{}')>".format(
            self.request_id, self.id
        )
