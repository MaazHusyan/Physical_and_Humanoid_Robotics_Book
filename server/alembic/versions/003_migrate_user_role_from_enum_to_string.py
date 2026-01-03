"""migrate user role from enum to string

Revision ID: 003_migrate_user_role_from_enum_to_string
Revises: 002_link_chat_to_users
Create Date: 2026-01-03 06:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '003_migrate_user_role_from_enum_to_string'
down_revision = '002_link_chat_to_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the userrole enum type if it exists
    op.execute("DROP TYPE IF EXISTS userrole;")

    # Alter the role column in users table to be VARCHAR instead of enum
    op.alter_column('users', 'role', type_=sa.String(50), postgresql_using="role::text")


def downgrade() -> None:
    # Recreate the userrole enum type
    op.execute("CREATE TYPE userrole AS ENUM ('student', 'admin');")

    # Change the role column back to enum type
    op.alter_column('users', 'role', type_=sa.Enum('student', 'admin', name='userrole'), postgresql_using="role::userrole")