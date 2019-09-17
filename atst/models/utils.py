from sqlalchemy import func, sql
from contextlib import contextmanager

from atst.database import db
from atst.domain.exceptions import ClaimFailedException


@contextmanager
def claim_for_update(resource):
    Model = resource.__class__

    rows_updated = (
        db.session.query(Model)
        .filter_by(id=resource.id, claimed_at=None)
        .update({"claimed_at": func.now()}, synchronize_session=False)
    )
    if rows_updated < 1:
        raise ClaimFailedException(resource)

    claimed = db.session.query(Model).filter_by(id=resource.id).one()

    try:
        yield claimed
    finally:
        db.session.query(Model).filter(Model.id == resource.id).filter(
            Model.claimed_at != None
        ).update({"claimed_at": sql.null()}, synchronize_session=False)
