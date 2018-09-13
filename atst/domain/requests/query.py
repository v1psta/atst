from sqlalchemy import exists, and_, exc, text

from atst.database import db
from atst.domain.common import Query
from atst.models.request import Request


class RequestsQuery(Query):
    model = Request

    @classmethod
    def exists(cls, request_id, creator):
        try:
            return db.session.query(
                exists().where(
                    and_(Request.id == request_id, Request.creator == creator)
                )
            ).scalar()

        except exc.DataError:
            return False

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
    def get_with_lock(cls, request_id):
        try:
            # Query for request matching id, acquiring a row-level write lock.
            # https://www.postgresql.org/docs/10/static/sql-select.html#SQL-FOR-UPDATE-SHARE
            return (
                db.session.query(Request)
                .filter_by(id=request_id)
                .with_for_update(of=Request)
                .one()
            )

        except NoResultFound:
            raise NotFoundError("requests")

    @classmethod
    def status_count(cls, status, creator=None):
        bindings = {"status": status.name}
        raw = """
SELECT count(requests_with_status.id)
FROM (
    SELECT DISTINCT ON (rse.request_id) r.*, rse.new_status as status
    FROM request_status_events rse JOIN requests r ON r.id = rse.request_id
    ORDER BY rse.request_id, rse.sequence DESC
) as requests_with_status
WHERE requests_with_status.status = :status
        """

        if creator:
            raw += " AND requests_with_status.user_id = :user_id"
            bindings["user_id"] = creator.id

        results = db.session.execute(text(raw), bindings).fetchone()
        (count,) = results
        return count
