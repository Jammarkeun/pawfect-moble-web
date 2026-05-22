"""Add rider_availability table

Revision ID: 2025_10_31_add_rider_availability
Revises: 
Create Date: 2025-10-31 13:38:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2025_10_31_add_rider_availability'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add ready_for_delivery to order status enum
    op.alter_column('orders', 'status',
                   existing_type=mysql.ENUM('pending', 'confirmed', 'preparing', 'shipped', 'delivered', 'cancelled'),
                   type_=mysql.ENUM('pending', 'confirmed', 'preparing', 'ready_for_delivery', 'shipped', 'assigned_to_rider', 'picked_up', 'on_the_way', 'delivered', 'cancelled'),
                   existing_nullable=False,
                   existing_server_default=sa.text("'pending'"))
    
    # Create rider_availability table
    op.create_table('rider_availability',
        sa.Column('id', mysql.INTEGER(11), autoincrement=True, nullable=False),
        sa.Column('rider_id', mysql.INTEGER(11), nullable=False),
        sa.Column('is_available', mysql.TINYINT(1), server_default=sa.text("1"), nullable=False),
        sa.Column('current_lat', mysql.DECIMAL(10, 8), nullable=True),
        sa.Column('current_lng', mysql.DECIMAL(11, 8), nullable=True),
        sa.Column('last_online', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('max_distance', mysql.INTEGER(11), server_default=sa.text("20"), nullable=True, comment='in km'),
        sa.ForeignKeyConstraint(['rider_id'], ['users.id'], name='fk_rider_availability_user', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rider_id', name='unique_rider'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index('idx_available', 'rider_availability', ['is_available', 'last_online'], unique=False)

def downgrade():
    op.drop_index('idx_available', table_name='rider_availability')
    op.drop_table('rider_availability')
    
    # Revert order status enum
    op.alter_column('orders', 'status',
                   existing_type=mysql.ENUM('pending', 'confirmed', 'preparing', 'ready_for_delivery', 'shipped', 'assigned_to_rider', 'picked_up', 'on_the_way', 'delivered', 'cancelled'),
                   type_=mysql.ENUM('pending', 'confirmed', 'preparing', 'shipped', 'delivered', 'cancelled'),
                   existing_nullable=False,
                   existing_server_default=sa.text("'pending'"))
