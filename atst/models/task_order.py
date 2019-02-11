from enum import Enum
from datetime import date

import pendulum
from sqlalchemy import Boolean, Column, Numeric, String, ForeignKey, Date, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import ARRAY
from sqlalchemy.orm import relationship
from werkzeug.datastructures import FileStorage

from atst.models import Attachment, Base, types, mixins


class Status(Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    EXPIRED = "Expired"


class TaskOrder(Base, mixins.TimestampsMixin):
    __tablename__ = "task_orders"

    id = types.Id()

    portfolio_id = Column(ForeignKey("portfolios.id"))
    portfolio = relationship("Portfolio")

    user_id = Column(ForeignKey("users.id"))
    creator = relationship("User", foreign_keys="TaskOrder.user_id")

    ko_id = Column(ForeignKey("users.id"))
    contracting_officer = relationship("User", foreign_keys="TaskOrder.ko_id")

    cor_id = Column(ForeignKey("users.id"))
    contracting_officer_representative = relationship(
        "User", foreign_keys="TaskOrder.cor_id"
    )

    so_id = Column(ForeignKey("users.id"))
    security_officer = relationship("User", foreign_keys="TaskOrder.so_id")

    scope = Column(String)  # Cloud Project Scope
    defense_component = Column(String)  # Department of Defense Component
    app_migration = Column(String)  # App Migration
    native_apps = Column(String)  # Native Apps
    complexity = Column(ARRAY(String))  # Application Complexity
    complexity_other = Column(String)
    dev_team = Column(ARRAY(String))  # Development Team
    dev_team_other = Column(String)
    team_experience = Column(String)  # Team Experience
    start_date = Column(Date)  # Period of Performance
    end_date = Column(Date)
    performance_length = Column(Integer)
    csp_attachment_id = Column(ForeignKey("attachments.id"))
    _csp_estimate = relationship("Attachment", foreign_keys=[csp_attachment_id])
    clin_01 = Column(Numeric(scale=2))
    clin_02 = Column(Numeric(scale=2))
    clin_03 = Column(Numeric(scale=2))
    clin_04 = Column(Numeric(scale=2))
    ko_first_name = Column(String)  # First Name
    ko_last_name = Column(String)  # Last Name
    ko_email = Column(String)  # Email
    ko_phone_number = Column(String)  # Phone Number
    ko_dod_id = Column(String)  # DOD ID
    ko_invite = Column(Boolean)
    cor_first_name = Column(String)  # First Name
    cor_last_name = Column(String)  # Last Name
    cor_email = Column(String)  # Email
    cor_phone_number = Column(String)  # Phone Number
    cor_dod_id = Column(String)  # DOD ID
    cor_invite = Column(Boolean)
    so_first_name = Column(String)  # First Name
    so_last_name = Column(String)  # Last Name
    so_email = Column(String)  # Email
    so_phone_number = Column(String)  # Phone Number
    so_dod_id = Column(String)  # DOD ID
    so_invite = Column(Boolean)
    pdf_attachment_id = Column(ForeignKey("attachments.id"))
    _pdf = relationship("Attachment", foreign_keys=[pdf_attachment_id])
    number = Column(String, unique=True)  # Task Order Number
    loa = Column(String)  # Line of Accounting (LOA)
    custom_clauses = Column(String)  # Custom Clauses

    @hybrid_property
    def csp_estimate(self):
        return self._csp_estimate

    @csp_estimate.setter
    def csp_estimate(self, new_csp_estimate):
        self._csp_estimate = self._set_attachment(new_csp_estimate, "_csp_estimate")

    @hybrid_property
    def pdf(self):
        return self._pdf

    @pdf.setter
    def pdf(self, new_pdf):
        self._pdf = self._set_attachment(new_pdf, "_pdf")

    def _set_attachment(self, new_attachment, attribute):
        if isinstance(new_attachment, Attachment):
            return new_attachment
        elif isinstance(new_attachment, FileStorage):
            return Attachment.attach(new_attachment, "task_order", self.id)
        elif not new_attachment and hasattr(self, attribute):
            return None
        else:
            raise TypeError("Could not set attachment with invalid type")

    @property
    def is_submitted(self):
        return (
            self.number is not None
            and self.start_date is not None
            and self.end_date is not None
        )

    @property
    def is_active(self):
        return self.status == Status.ACTIVE

    @property
    def status(self):
        if self.is_submitted:
            now = pendulum.now().date()
            if self.start_date > now:
                return Status.PENDING
            elif self.end_date < now:
                return Status.EXPIRED
            return Status.ACTIVE
        else:
            return Status.PENDING

    @property
    def display_status(self):
        return self.status.value

    @property
    def days_to_expiration(self):
        if self.end_date:
            return (self.end_date - date.today()).days

    @property
    def budget(self):
        return sum(
            filter(None, [self.clin_01, self.clin_02, self.clin_03, self.clin_04])
        )

    @property
    def balance(self):
        # TODO: somehow calculate the remaining balance. For now, assume $0 spent
        return self.budget

    @property
    def portfolio_name(self):
        return self.portfolio.name

    @property
    def is_pending(self):
        return self.status == Status.PENDING

    @property
    def ko_invitable(self):
        """
        The MO has indicated that the KO should be invited but we have not sent
        an invite and attached the KO user
        """
        return self.ko_invite and not self.contracting_officer

    @property
    def cor_invitable(self):
        """
        The MO has indicated that the COR should be invited but we have not sent
        an invite and attached the COR user
        """
        return self.cor_invite and not self.contracting_officer_representative

    @property
    def so_invitable(self):
        """
        The MO has indicated that the SO should be invited but we have not sent
        an invite and attached the SO user
        """
        return self.so_invite and not self.security_officer

    _OFFICER_PREFIXES = {
        "contracting_officer": "ko",
        "contracting_officer_representative": "cor",
        "security_officer": "so",
    }
    _OFFICER_PROPERTIES = ["first_name", "last_name", "phone_number", "email", "dod_id"]

    def officer_dictionary(self, officer_type):
        prefix = self._OFFICER_PREFIXES[officer_type]
        return {
            field: getattr(self, "{}_{}".format(prefix, field))
            for field in self._OFFICER_PROPERTIES
        }

    def to_dictionary(self):
        return {
            "portfolio_name": self.portfolio_name,
            **{
                c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name not in ["id"]
            },
        }

    def __repr__(self):
        return "<TaskOrder(number='{}', budget='{}', end_date='{}', id='{}')>".format(
            self.number, self.budget, self.end_date, self.id
        )
