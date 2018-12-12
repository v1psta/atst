"""stop updates of dod id

Revision ID: c222327c3963
Revises: 02d11579a581
Create Date: 2018-12-12 10:23:00.773973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c222327c3963'
down_revision = '02d11579a581'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
CREATE OR REPLACE FUNCTION lock_dod_id()
RETURNS TRIGGER
AS $$
BEGIN
    IF NEW.dod_id != OLD.dod_id THEN
        RAISE EXCEPTION 'DOD ID cannot be updated';
    END IF;

    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER lock_dod_id
BEFORE UPDATE ON users
FOR EACH ROW
    EXECUTE PROCEDURE lock_dod_id();
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
DROP TRIGGER IF EXISTS lock_dod_id ON users;
DROP FUNCTION IF EXISTS lock_dod_id();
    """)
