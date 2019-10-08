"""add deleted environment_role status

Revision ID: 1497926ddec1
Revises: e3d93f9caba7
Create Date: 2019-10-04 10:44:54.198368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1497926ddec1"  # pragma: allowlist secret
down_revision = "f50596c5ffbb"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "environment_roles",
        "status",
        type_=sa.Enum(
            "PENDING",
            "COMPLETED",
            "PENDING_DELETE",
            "DELETED",
            name="status",
            native_enum=False,
        ),
        existing_type=sa.Enum(
            "PENDING", "COMPLETED", "PENDING_DELETE", name="status", native_enum=False
        ),
    )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        """
        UPDATE environment_roles
        SET status = (CASE WHEN status = 'DELETED' THEN 'PENDING_DELETE' ELSE status END)
        """
    )
    op.alter_column(
        "environment_roles",
        "status",
        type_=sa.Enum(
            "PENDING", "COMPLETED", "PENDING_DELETE", name="status", native_enum=False
        ),
        existing_type=sa.Enum(
            "PENDING",
            "COMPLETED",
            "PENDING_DELETE",
            "DELETED",
            name="status",
            native_enum=False,
        ),
    )
