"""environment_roles has relation to application_roles

Revision ID: d2390c547dca
Revises: ab1167fc8260
Create Date: 2019-05-29 12:34:45.928219

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd2390c547dca'
down_revision = 'ab1167fc8260'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    op.add_column('environment_roles', sa.Column('application_role_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.drop_index('environments_role_user_environment', table_name='environment_roles')
    op.create_index('environments_role_user_environment', 'environment_roles', ['application_role_id', 'environment_id'], unique=True)
    op.drop_constraint('environment_roles_user_id_fkey', 'environment_roles', type_='foreignkey')
    op.create_foreign_key("environment_roles_application_roles_fkey", 'environment_roles', 'application_roles', ['application_role_id'], ['id'])
    conn.execute("""
UPDATE environment_roles er
SET application_role_id = application_roles.id
FROM environments, applications, application_roles
WHERE
    environment_id = environments.id AND
    applications.id = environments.application_id AND
    application_roles.application_id = applications.id AND
    er.user_id = application_roles.user_id;
""")
    op.alter_column('environment_roles', "application_role_id", nullable=False)
    op.drop_column('environment_roles', 'user_id')


def downgrade():
    conn = op.get_bind()
    op.add_column('environment_roles', sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=True))
    op.drop_constraint("environment_roles_application_roles_fkey", 'environment_roles', type_='foreignkey')
    op.create_foreign_key('environment_roles_user_id_fkey', 'environment_roles', 'users', ['user_id'], ['id'])
    op.drop_index('environments_role_user_environment', table_name='environment_roles')
    op.create_index('environments_role_user_environment', 'environment_roles', ['user_id', 'environment_id'], unique=True)
    conn.execute("""
UPDATE environment_roles
SET user_id = application_roles.user_id
FROM application_roles
WHERE application_role_id = application_roles.id
""")
    op.alter_column('environment_roles', "user_id", nullable=False)
    op.drop_column('environment_roles', 'application_role_id')
