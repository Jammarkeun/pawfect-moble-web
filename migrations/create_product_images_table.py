"""
Migration script to create product_images table for multiple images per product
Run this script to add support for multiple product images
"""

import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.database import Database

def create_product_images_table():
    """Create the product_images table"""
    db = Database()
    
    try:
        # Create product_images table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS product_images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            image_url VARCHAR(500) NOT NULL,
            display_order INT DEFAULT 0,
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            INDEX idx_product_id (product_id),
            INDEX idx_display_order (display_order)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        db.execute_query(create_table_query)
        print("✓ Created product_images table")
        
        # Migrate existing product images to the new table
        # First check if there are any products with images that haven't been migrated
        check_query = """
        SELECT COUNT(*) as count FROM products p
        WHERE p.image_url IS NOT NULL AND p.image_url != ''
        AND NOT EXISTS (
            SELECT 1 FROM product_images pi WHERE pi.product_id = p.id
        )
        """
        result = db.execute_query(check_query, fetch=True, fetchone=True)
        
        if result and result['count'] > 0:
            migrate_query = """
            INSERT INTO product_images (product_id, image_url, display_order, is_primary)
            SELECT p.id, p.image_url, 0, TRUE
            FROM products p
            WHERE p.image_url IS NOT NULL AND p.image_url != ''
            AND NOT EXISTS (
                SELECT 1 FROM product_images pi WHERE pi.product_id = p.id
            )
            """
            
            db.execute_query(migrate_query)
            print(f"✓ Migrated {result['count']} existing product images to product_images table")
        else:
            print("✓ No products to migrate or already migrated")
        
        print("\n✅ Migration completed successfully!")
        print("Products now support multiple images with swipeable galleries.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == '__main__':
    print("Starting migration: Create product_images table...")
    create_product_images_table()
