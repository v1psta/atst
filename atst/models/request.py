from sqlalchemy import Column, func, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins
from atst.models.request_status_event import RequestStatus
from atst.utils import first_or_none
from atst.models.request_revision import RequestRevision
from atst.models.task_order import Source as TaskOrderSource


def map_properties_to_dict(properties, instance):
    return {
        field: getattr(instance, field)
        for field in properties
        if getattr(instance, field) is not None
    }


def update_dict_with_properties(instance, body, top_level_key, properties):
    new_properties = map_properties_to_dict(properties, instance)
    if new_properties:
        body[top_level_key] = new_properties

    return body


class Request(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "requests"

    id = types.Id()
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    status_events = relationship(
        "RequestStatusEvent", backref="request", order_by="RequestStatusEvent.sequence"
    )

    workspace = relationship("Workspace", uselist=False, backref="request")

    user_id = Column(ForeignKey("users.id"), nullable=False)
    creator = relationship("User", backref="owned_requests")

    task_order_id = Column(ForeignKey("task_orders.id"))
    task_order = relationship("TaskOrder")

    revisions = relationship(
        "RequestRevision", back_populates="request", order_by="RequestRevision.sequence"
    )

    internal_comments = relationship("RequestInternalComment")

    @property
    def latest_revision(self):
        if self.revisions:
            return self.revisions[-1]

        else:
            return RequestRevision(request=self)

    PRIMARY_POC_FIELDS = ["am_poc", "dodid_poc", "email_poc", "fname_poc", "lname_poc"]
    DETAILS_OF_USE_FIELDS = [
        "jedi_usage",
        "start_date",
        "cloud_native",
        "dollar_value",
        "dod_component",
        "data_transfers",
        "expected_completion_date",
        "jedi_migration",
        "num_software_systems",
        "number_user_sessions",
        "average_daily_traffic",
        "engineering_assessment",
        "technical_support_team",
        "estimated_monthly_spend",
        "average_daily_traffic_gb",
        "rationalization_software_systems",
        "organization_providing_assistance",
        "name",
    ]
    INFORMATION_ABOUT_YOU_FIELDS = [
        "citizenship",
        "designation",
        "phone_number",
        "email_request",
        "fname_request",
        "lname_request",
        "service_branch",
        "date_latest_training",
    ]
    FINANCIAL_VERIFICATION_FIELDS = [
        "pe_id",
        "task_order_number",
        "fname_co",
        "lname_co",
        "email_co",
        "office_co",
        "fname_cor",
        "lname_cor",
        "email_cor",
        "office_cor",
        "uii_ids",
        "treasury_code",
        "ba_code",
    ]

    @property
    def body(self):
        current = self.latest_revision
        body = {}
        for top_level_key, properties in [
            ("primary_poc", Request.PRIMARY_POC_FIELDS),
            ("details_of_use", Request.DETAILS_OF_USE_FIELDS),
            ("information_about_you", Request.INFORMATION_ABOUT_YOU_FIELDS),
            ("financial_verification", Request.FINANCIAL_VERIFICATION_FIELDS),
        ]:
            body = update_dict_with_properties(current, body, top_level_key, properties)

        return body

    @property
    def latest_status(self):
        return self.status_events[-1] if self.status_events else None

    @property
    def status(self):
        return self.latest_status.new_status if self.latest_status else None

    @property
    def status_displayname(self):
        return self.latest_status.displayname

    @property
    def annual_spend(self):
        monthly = self.latest_revision.estimated_monthly_spend or 0
        return monthly * 12

    @property
    def financial_verification(self):
        return self.body.get("financial_verification", {})

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
            return last_submission.time_created
        return None

    @property
    def action_required_by(self):
        return {
            RequestStatus.PENDING_FINANCIAL_VERIFICATION: "mission_owner",
            RequestStatus.CHANGES_REQUESTED: "mission_owner",
            RequestStatus.CHANGES_REQUESTED_TO_FINVER: "mission_owner",
            RequestStatus.PENDING_CCPO_APPROVAL: "ccpo",
            RequestStatus.PENDING_CCPO_ACCEPTANCE: "ccpo",
        }.get(self.status)

    @property
    def reviews(self):
        return [status.review for status in self.status_events if status.review]

    @property
    def is_pending_financial_verification(self):
        return self.status == RequestStatus.PENDING_FINANCIAL_VERIFICATION

    @property
    def is_pending_financial_verification_changes(self):
        return self.status == RequestStatus.CHANGES_REQUESTED_TO_FINVER

    @property
    def is_pending_ccpo_acceptance(self):
        return self.status == RequestStatus.PENDING_CCPO_ACCEPTANCE

    @property
    def is_pending_ccpo_approval(self):
        return self.status == RequestStatus.PENDING_CCPO_APPROVAL

    @property
    def is_pending_ccpo_action(self):
        return self.is_pending_ccpo_acceptance or self.is_pending_ccpo_approval

    @property
    def is_approved(self):
        return self.status == RequestStatus.APPROVED

    @property
    def review_comment(self):
        if (
            self.status == RequestStatus.CHANGES_REQUESTED
            or self.status == RequestStatus.CHANGES_REQUESTED_TO_FINVER
        ):
            review = self.latest_status.review
            if review:
                return review.comment

    @property
    def has_financial_data(self):
        return (
            self.is_pending_ccpo_approval
            or self.is_pending_financial_verification_changes
            or self.is_approved
        ) and self.task_order

    @property
    def displayname(self):
        return self.latest_revision.name or self.id

    @property
    def contracting_officer_full_name(self):
        if self.latest_revision.fname_co:
            return "{} {}".format(
                self.latest_revision.fname_co, self.latest_revision.lname_co
            )

    @property
    def contracting_officer_email(self):
        return self.latest_revision.email_co

    @property
    def pe_number(self):
        return self.body.get("financial_verification", {}).get("pe_id")

    @property
    def has_manual_task_order(self):
        return (
            self.task_order.source == TaskOrderSource.MANUAL
            if self.task_order is not None
            else None
        )

    @property
    def simple_status(self):
        return self.latest_status.simple_name

    def __repr__(self):
        return "<Request(status='{}', name='{}', creator='{}', is_approved='{}', time_created='{}', id='{}')>".format(
            self.status_displayname,
            self.displayname,
            self.creator.full_name,
            self.is_approved,
            self.time_created,
            self.id,
        )
