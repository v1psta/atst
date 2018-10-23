import dateutil

from atst.domain.workspaces import Workspaces
from atst.models.request_revision import RequestRevision
from atst.models.request_status_event import RequestStatusEvent, RequestStatus
from atst.models.request_review import RequestReview
from atst.models.request_internal_comment import RequestInternalComment
from atst.utils import deep_merge

from .query import RequestsQuery
from .authorization import RequestsAuthorization


def create_revision_from_request_body(body):
    body = {k: v for p in body.values() for k, v in p.items()}
    DATES = ["start_date", "date_latest_training"]
    coerced_timestamps = {
        k: dateutil.parser.parse(v)
        for k, v in body.items()
        if k in DATES and isinstance(v, str)
    }
    body = {**body, **coerced_timestamps}
    return RequestRevision(**body)


class Requests(object):
    AUTO_APPROVE_THRESHOLD = 1_000_000
    ANNUAL_SPEND_THRESHOLD = 1_000_000

    @classmethod
    def create(cls, creator, body):
        revision = create_revision_from_request_body(body)
        request = RequestsQuery.create(creator=creator, revisions=[revision])
        request = Requests.set_status(request, RequestStatus.STARTED)
        request = RequestsQuery.add_and_commit(request)

        return request

    @classmethod
    def exists(cls, request_id, creator):
        return RequestsQuery.exists(request_id, creator)

    @classmethod
    def get(cls, user, request_id):
        request = RequestsQuery.get(request_id)
        RequestsAuthorization(user, request).check_can_view("get request")
        return request

    @classmethod
    def get_for_approval(cls, user, request_id):
        request = RequestsQuery.get(request_id)
        RequestsAuthorization(user, request).check_can_approve()
        return request

    @classmethod
    def get_many(cls, creator=None):
        return RequestsQuery.get_many(creator)

    @classmethod
    def submit(cls, request):
        request = Requests.set_status(request, RequestStatus.SUBMITTED)

        new_status = None
        if Requests.should_auto_approve(request):
            new_status = RequestStatus.PENDING_FINANCIAL_VERIFICATION
        else:
            new_status = RequestStatus.PENDING_CCPO_ACCEPTANCE

        request = Requests.set_status(request, new_status)
        request = RequestsQuery.add_and_commit(request)

        return request

    @classmethod
    def update(cls, request_id, request_delta):
        request = RequestsQuery.get_with_lock(request_id)
        return Requests._update(request, request_delta)

    @classmethod
    def _update(cls, request, request_delta):
        new_body = deep_merge(request_delta, request.body)
        revision = create_revision_from_request_body(new_body)
        request.revisions.append(revision)

        return RequestsQuery.add_and_commit(request)

    @classmethod
    def approve_and_create_workspace(cls, request):
        approved_request = Requests.set_status(request, RequestStatus.APPROVED)
        workspace = Workspaces.create(approved_request)

        RequestsQuery.add_and_commit(approved_request)

        return workspace

    @classmethod
    def set_status(cls, request, status: RequestStatus):
        status_event = RequestStatusEvent(
            new_status=status, revision=request.latest_revision
        )
        request.status_events.append(status_event)
        return request

    @classmethod
    def should_auto_approve(cls, request):
        try:
            dollar_value = request.body["details_of_use"]["dollar_value"]
        except KeyError:
            return False

        return dollar_value < cls.AUTO_APPROVE_THRESHOLD

    _VALID_SUBMISSION_STATUSES = [
        RequestStatus.STARTED,
        RequestStatus.CHANGES_REQUESTED,
    ]

    @classmethod
    def should_allow_submission(cls, request):
        all_request_sections = [
            "details_of_use",
            "information_about_you",
            "primary_poc",
        ]
        existing_request_sections = request.body.keys()
        return request.status in Requests._VALID_SUBMISSION_STATUSES and all(
            section in existing_request_sections for section in all_request_sections
        )

    @classmethod
    def status_count(cls, status, creator=None):
        return RequestsQuery.status_count(status, creator)

    @classmethod
    def in_progress_count(cls):
        return sum(
            [
                Requests.status_count(RequestStatus.STARTED),
                Requests.status_count(RequestStatus.PENDING_FINANCIAL_VERIFICATION),
                Requests.status_count(RequestStatus.CHANGES_REQUESTED),
            ]
        )

    @classmethod
    def pending_ccpo_count(cls):
        return sum(
            [
                Requests.status_count(RequestStatus.PENDING_CCPO_ACCEPTANCE),
                Requests.status_count(RequestStatus.PENDING_CCPO_APPROVAL),
            ]
        )

    @classmethod
    def completed_count(cls):
        return Requests.status_count(RequestStatus.APPROVED)

    @classmethod
    def update_financial_verification(cls, request_id, financial_data, task_order=None):
        request = RequestsQuery.get_with_lock(request_id)

        if task_order:
            request.task_order = task_order

        request = Requests._update(request, {"financial_verification": financial_data})
        return request

    @classmethod
    def submit_financial_verification(cls, request):
        request = Requests.set_status(request, RequestStatus.PENDING_CCPO_APPROVAL)
        request = RequestsQuery.add_and_commit(request)
        return request

    @classmethod
    def _add_review(cls, user, request, review_data):
        request.latest_status.review = RequestReview(reviewer=user, **review_data)
        request = RequestsQuery.add_and_commit(request)
        return request

    @classmethod
    def advance(cls, user, request, review_data):
        if request.status == RequestStatus.PENDING_CCPO_ACCEPTANCE:
            Requests.set_status(request, RequestStatus.PENDING_FINANCIAL_VERIFICATION)
        elif request.status == RequestStatus.PENDING_CCPO_APPROVAL:
            Requests.approve_and_create_workspace(request)

        return Requests._add_review(user, request, review_data)

    @classmethod
    def request_changes(cls, user, request, review_data):
        if request.status == RequestStatus.PENDING_CCPO_ACCEPTANCE:
            Requests.set_status(request, RequestStatus.CHANGES_REQUESTED)
        elif request.status == RequestStatus.PENDING_CCPO_APPROVAL:
            Requests.set_status(request, RequestStatus.CHANGES_REQUESTED_TO_FINVER)

        return Requests._add_review(user, request, review_data)

    @classmethod
    def add_internal_comment(cls, user, request, comment_text):
        RequestsAuthorization(user, request).check_can_approve()
        comment = RequestInternalComment(request=request, text=comment_text, user=user)
        RequestsQuery.add_and_commit(comment)
        return request
