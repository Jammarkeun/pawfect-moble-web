"""add rider availability table

Revision ID: 1234abcd5678
Revises: previous_migration_id
Create Date: 2025-10-30 11:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1234abcd5678'
down_revision = 'previous_migration_id'
branch_labels = None
depends_on = None

def upgrade():
    # Create rider_availability table
    op.create_table(
        'rider_availability',
        sa.Column('rider_id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('is_online', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('last_seen', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('current_location', sa.Text(), nullable=True),  # Using Text to store 'POINT(lng,lat)'
        sa.ForeignKeyConstraint(['rider_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('rider_id')
    )
    
    # Add status column to orders if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        BEGIN
            ALTER TABLE orders ADD COLUMN status VARCHAR(20) 
                DEFAULT 'pending' 
                CHECK (status IN ('pending', 'confirmed', 'shipped', 'out_for_delivery', 'delivered', 'cancelled'));
        EXCEPTION
            WHEN duplicate_column THEN 
                RAISE NOTICE 'column status already exists in orders';
        END;
    END $$;
    """)
    
    # Create index for faster lookups
    op.create_index(op.f('ix_rider_availability_is_online'), 'rider_availability', ['is_online'], unique=False)

def downgrade():
    # Drop the index
    op.drop_index(op.f('ix_rider_availability_is_online'), table_name='rider_availability')
    
    # Drop the table
    op.drop_table('rider_availability')
    
    # Note: We don't drop the status column from orders as it might contain data
