from sqlalchemy import func, sql, Interval, and_, or_
from contextlib import contextmanager

from atst.database import db
from atst.domain.exceptions import ClaimFailedException


@contextmanager
def claim_for_update(resource, minutes=30):
    """
    Claim a mutually exclusive expiring hold on a resource.
    Uses the database as a central source of time in case the server clocks have drifted.

    Args:
        resource:   A SQLAlchemy model instance with a `claimed_until` attribute.
        minutes:    The maximum amount of time, in minutes, to hold the claim.
    """
    Model = resource.__class__

    claim_until = func.now() + func.cast(
        sql.functions.concat(minutes, " MINUTES"), Interval
    )

    # Optimistically query for and update the resource in question. If it's
    # already claimed, `rows_updated` will be 0 and we can give up.
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

    # Fetch the claimed resource
    claimed = db.session.query(Model).filter_by(id=resource.id).one()

    try:
        # Give the resource to the caller.
        yield claimed
    finally:
        # Release the claim.
        db.session.query(Model).filter(Model.id == resource.id).filter(
            Model.claimed_until != None
        ).update({"claimed_until": None}, synchronize_session="fetch")
