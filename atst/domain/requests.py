from sqlalchemy import exists, and_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.attributes import flag_modified

from atst.models.request import Request
from atst.models.request_status_event import RequestStatusEvent, RequestStatus
from atst.database import db

from .exceptions import NotFoundError


def deep_merge(source, destination: dict):
    """
    Merge source dict into destination dict recursively.
    """

    def _deep_merge(a, b):
        for key, value in a.items():
            if isinstance(value, dict):
                node = b.setdefault(key, {})
                _deep_merge(value, node)
            else:
                b[key] = value

        return b

    return _deep_merge(source, dict(destination))


class Requests(object):
    AUTO_APPROVE_THRESHOLD = 1000000

    @classmethod
    def create(cls, creator_id, body):
        request = Request(creator=creator_id, body=body)
        request = Requests.set_status(request, RequestStatus.STARTED)

        db.session.add(request)
        db.session.commit()

        return request

    @classmethod
    def exists(cls, request_id, creator_id):
        return db.session.query(
            exists().where(
                and_(Request.id == request_id, Request.creator == creator_id)
            )
        ).scalar()

    @classmethod
    def get(cls, request_id):
        try:
            request = db.session.query(Request).filter_by(id=request_id).one()
        except NoResultFound:
            raise NotFoundError("request")

        return request

    @classmethod
    def get_many(cls, creator=None):
        filters = []
        if creator:
            filters.append(Request.creator == creator)

        requests = (
            db.session.query(Request)
            .filter(*filters)
            .order_by(Request.time_created.desc())
            .all()
        )
        return requests

    @classmethod
    def submit(cls, request):
        new_status = None
        if Requests.should_auto_approve(request):
            new_status = RequestStatus.PENDING_FINANCIAL_VERIFICATION
        else:
            new_status = RequestStatus.PENDING_CCPO_APPROVAL

        request = Requests.set_status(request, new_status)

        db.session.add(request)
        db.session.commit()

        return request

    @classmethod
    def update(cls, request_id, request_delta):
        try:
            # Query for request matching id, acquiring a row-level write lock.
            # https://www.postgresql.org/docs/10/static/sql-select.html#SQL-FOR-UPDATE-SHARE
            request = (
                db.session.query(Request)
                .filter_by(id=request_id)
                .with_for_update(of=Request)
                .one()
            )
        except NoResultFound:
            return

        request.body = deep_merge(request_delta, request.body)

        # Without this, sqlalchemy won't notice the change to request.body,
        # since it doesn't track dictionary mutations by default.
        flag_modified(request, "body")

        db.session.add(request)
        db.session.commit()

    @classmethod
    def set_status(cls, request: Request, status: RequestStatus):
        status_event = RequestStatusEvent(new_status=status)
        request.status_events.append(status_event)
        return request

    @classmethod
    def action_required_by(cls, request):
        return {
            RequestStatus.STARTED: "mission_owner",
            RequestStatus.PENDING_FINANCIAL_VERIFICATION: "mission_owner",
            RequestStatus.PENDING_CCPO_APPROVAL: "ccpo"
        }.get(request.status)

    @classmethod
    def should_auto_approve(cls, request):
        try:
            dollar_value = request.body["details_of_use"]["dollar_value"]
        except KeyError:
            return False

        return dollar_value < cls.AUTO_APPROVE_THRESHOLD

    @classmethod
    def should_allow_submission(cls, request):
        all_request_sections = [
            "details_of_use",
            "information_about_you",
            "primary_poc",
        ]
        existing_request_sections = request.body.keys()
        return request.status == "incomplete" and all(
            section in existing_request_sections for section in all_request_sections
        )
