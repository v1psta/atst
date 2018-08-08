"""new request statuses

Revision ID: 77b065750596
Revises: 1f57f784ed5b
Create Date: 2018-08-07 16:42:11.502361

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import sessionmaker

from atst.models.request_status_event import RequestStatus


# revision identifiers, used by Alembic.
revision = '77b065750596'
down_revision = '1f57f784ed5b'
branch_labels = None
depends_on = None


def upgrade():
    """
    Update all existing request statuses so that the state of the
    table reflects the statuses listed in RequestStatus.

    This involves fixing the casing on existing statuses, and
    deleting statuses that have no match.
    """

    db = op.get_bind()

    status_events = db.execute("SELECT * FROM request_status_events").fetchall()
    for status_event in status_events:
        try:
            status = RequestStatus[status_event["new_status"].upper()]
            query = sa.text("""
                UPDATE request_status_events
                SET new_status = :status
                WHERE id = :id"""
            )
            db.execute(query, id=status_event["id"], status=status.name)
        except ValueError:
            query = sa.text("DELETE FROM request_status_events WHERE id = :id")
            db.execute(query, id=status_event["id"])


def downgrade():
    pass
