"""Add location fields to users and products

Revision ID: 2025_10_31_add_location_fields
Revises: 2025_10_31_add_shipping_fee
Create Date: 2025-10-31 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025_10_31_add_location_fields'
down_revision = '2025_10_31_add_shipping_fee'
branch_labels = None
depends_on = None

def upgrade():
    # Add location fields to users table
    op.add_column('users', sa.Column('latitude', sa.Numeric(10, 8), nullable=True))
    op.add_column('users', sa.Column('longitude', sa.Numeric(11, 8), nullable=True))
    
    # Add location fields to products table
    op.add_column('products', sa.Column('seller_latitude', sa.Numeric(10, 8), nullable=True))
    op.add_column('products', sa.Column('seller_longitude', sa.Numeric(11, 8), nullable=True))
    
    # Set default location for existing users (Manila coordinates)
    op.execute("""
        UPDATE users 
        SET latitude = 14.5995, 
            longitude = 120.9842
        WHERE latitude IS NULL OR longitude IS NULL
    """)
    
    # Set default location for existing products (Manila coordinates)
    op.execute("""
        UPDATE products p
        JOIN users u ON p.seller_id = u.id
        SET p.seller_latitude = u.latitude,
            p.seller_longitude = u.longitude
        WHERE p.seller_latitude IS NULL OR p.seller_longitude IS NULL
    """)

def downgrade():
    op.drop_column('users', 'longitude')
    op.drop_column('users', 'latitude')
    op.drop_column('products', 'seller_longitude')
    op.drop_column('products', 'seller_latitude')
