"""adjust invitation status

Revision ID: e1081cf01780
Revises: a9d8c6b6221c
Create Date: 2018-11-01 12:24:10.970963

"""
from alembic import op
import sqlalchemy as sa
from atst.models.invitation import Status
from enum import Enum


# revision identifiers, used by Alembic.
revision = 'e1081cf01780'
down_revision = 'a9d8c6b6221c'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    constraints = ", ".join(["'{}'::character varying::text".format(s.name) for s in Status])
    conn.execute("ALTER TABLE invitations ALTER COLUMN status TYPE varchar(30)")
    conn.execute("ALTER TABLE invitations DROP CONSTRAINT status")
    conn.execute("ALTER TABLE invitations ADD CONSTRAINT status CHECK(status::text = ANY (ARRAY[{}]))".format(constraints))

class PreviousStatus(Enum):
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    PENDING = "pending"
    REJECTED = "rejected"

def downgrade():
    conn = op.get_bind()
    constraints = ", ".join(["'{}'::character varying::text".format(s.name) for s in PreviousStatus])
    conn.execute("ALTER TABLE invitations ALTER COLUMN status TYPE varchar(8)")
    conn.execute("ALTER TABLE invitations DROP CONSTRAINT status")
    conn.execute("ALTER TABLE invitations ADD CONSTRAINT status CHECK(status::text = ANY (ARRAY[{}]))".format(constraints))
