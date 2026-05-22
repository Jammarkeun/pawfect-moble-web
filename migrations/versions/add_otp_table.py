"""Add OTP table

Revision ID: add_otp_table
Revises: 
Create Date: 2025-10-29 17:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_otp_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create OTP table
    op.create_table(
        'otp_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('otp_code', sa.String(6), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), default=False, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_otp_email', 'email'),
        sa.Index('idx_otp_code', 'otp_code')
    )

def downgrade():
    op.drop_table('otp_codes')
