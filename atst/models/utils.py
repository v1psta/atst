from sqlalchemy import func, sql, Interval, and_, or_
from contextlib import contextmanager

from atst.database import db
from atst.domain.exceptions import ClaimFailedException


@contextmanager
def claim_for_update(resource, minutes=30):
    Model = resource.__class__

    claim_until = func.now() + func.cast(
        sql.functions.concat(minutes, " MINUTES"), Interval
    )

    rows_updated = (
        db.session.query(Model)
        .filter(
            and_(
                Model.id == resource.id,
                or_(Model.claimed_until == None, Model.claimed_until < func.now()),
            )
        )
        .update({"claimed_until": claim_until}, synchronize_session="fetch")
    )
    if rows_updated < 1:
        raise ClaimFailedException(resource)

    claimed = db.session.query(Model).filter_by(id=resource.id).one()

    try:
        yield claimed
    finally:
        db.session.query(Model).filter(Model.id == resource.id).filter(
            Model.claimed_until != None
        ).update({"claimed_until": None}, synchronize_session="fetch")
