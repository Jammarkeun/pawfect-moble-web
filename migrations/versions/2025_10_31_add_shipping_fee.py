"""Add shipping fee to orders

Revision ID: 2025_10_31_add_shipping_fee
Revises: 2025_10_31_add_rider_availability
Create Date: 2025-10-31 19:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025_10_31_add_shipping_fee'
down_revision = '2025_10_31_add_rider_availability'
branch_labels = None
depends_on = None

def upgrade():
    # Add shipping_fee, shipping_provider, and tracking_number columns to orders table
    op.add_column('orders', sa.Column('shipping_fee', sa.Numeric(10, 2), nullable=False, server_default='50.00'))
    op.add_column('orders', sa.Column('shipping_provider', sa.String(50), nullable=True))
    op.add_column('orders', sa.Column('tracking_number', sa.String(100), nullable=True))
    
    # Create a new shipping_providers table
    op.create_table(
        'shipping_providers',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('base_fee', sa.Numeric(10, 2), nullable=False),
        sa.Column('fee_per_km', sa.Numeric(10, 2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Insert default shipping providers
    op.execute("""
        INSERT INTO shipping_providers (name, base_fee, fee_per_km, is_active) VALUES
        ('J&T Express', 50.00, 5.00, 1),
        ('Ninja Van', 55.00, 6.00, 1),
        ('Lalamove', 60.00, 8.00, 1),
        ('LBC Express', 65.00, 7.00, 1),
        ('2GO', 45.00, 5.50, 1)
    """)

def downgrade():
    op.drop_column('orders', 'tracking_number')
    op.drop_column('orders', 'shipping_provider')
    op.drop_column('orders', 'shipping_fee')
    op.drop_table('shipping_providers')
