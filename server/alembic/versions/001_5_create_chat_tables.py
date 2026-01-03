"""create chat tables

Revision ID: 001_5_create_chat_tables
Revises: 001_create_auth_tables
Create Date: 2026-01-02 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_5_create_chat_tables'
down_revision = '001_create_auth_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create message_role enum type
    message_role_enum = postgresql.ENUM('user', 'assistant', name='messagerole', create_type=False)
    message_role_enum.create(op.get_bind(), checkfirst=True)

    # Create chat_sessions table
    op.create_table('chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),  # Will link to users table later
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        # No foreign key constraint yet since users table might not be created in this order
    )

    # Create indexes for chat_sessions table
    op.create_index('idx_chat_sessions_user_id', 'chat_sessions', ['user_id'])
    op.create_index('idx_chat_sessions_title', 'chat_sessions', ['title'])
    op.create_index('idx_chat_sessions_created_at', 'chat_sessions', ['created_at'])
    op.create_index('idx_chat_sessions_updated_at', 'chat_sessions', ['updated_at'])

    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', message_role_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE')
    )

    # Create indexes for chat_messages table
    op.create_index('idx_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('idx_chat_messages_role', 'chat_messages', ['role'])
    op.create_index('idx_chat_messages_created_at', 'chat_messages', ['created_at'])
    op.create_index('idx_chat_messages_model_used', 'chat_messages', ['model_used'])
    op.create_index('idx_chat_messages_tokens_used', 'chat_messages', ['tokens_used'])


def downgrade() -> None:
    # Drop chat_messages table
    op.drop_index('idx_chat_messages_tokens_used', table_name='chat_messages')
    op.drop_index('idx_chat_messages_model_used', table_name='chat_messages')
    op.drop_index('idx_chat_messages_created_at', table_name='chat_messages')
    op.drop_index('idx_chat_messages_role', table_name='chat_messages')
    op.drop_index('idx_chat_messages_session_id', table_name='chat_messages')
    op.drop_table('chat_messages')

    # Drop chat_sessions table
    op.drop_index('idx_chat_sessions_updated_at', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_created_at', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_title', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_user_id', table_name='chat_sessions')
    op.drop_table('chat_sessions')

    # Drop message_role enum type
    op.execute("DROP TYPE IF EXISTS messagerole;")