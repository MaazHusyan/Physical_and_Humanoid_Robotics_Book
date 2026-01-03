"""link chat to users

Revision ID: 002_link_chat_to_users
Revises: 001_5_create_chat_tables
Create Date: 2026-01-02 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '002_link_chat_to_users'
down_revision = '001_5_create_chat_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add foreign key constraint to existing user_id column
    op.create_foreign_key(
        'fk_chat_sessions_user_id',
        'chat_sessions',
        'users',
        ['user_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Create index for user_id and updated_at for efficient retrieval
    op.create_index('idx_chat_sessions_user_id_updated_at', 'chat_sessions', ['user_id', 'updated_at'], unique=False)


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_chat_sessions_user_id_updated_at', table_name='chat_sessions')

    # Drop foreign key constraint
    op.drop_constraint('fk_chat_sessions_user_id', 'chat_sessions', type_='foreignkey')