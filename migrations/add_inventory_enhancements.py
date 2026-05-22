"""
Database migration: Add inventory management enhancements
- Add cost_price to products and product_variants
- Ensure inventory_transactions table exists
- Ensure low_stock_alerts table exists
- Add low_stock_threshold to products
- Add product enhancement fields (slug, sku, sale dates, SEO fields, draft status)
"""

from app.services.database import Database
import logging

def migrate():
    db = Database()
    
    try:
        # 1. Add missing product fields
        print("📝 Adding enhanced product fields...")
        db.execute_query("""
            ALTER TABLE products
                ADD COLUMN IF NOT EXISTS cost_price DECIMAL(10,2) NULL COMMENT 'Cost/purchase price for valuation',
                ADD COLUMN IF NOT EXISTS low_stock_threshold INT DEFAULT 10 COMMENT 'Alert when stock falls below this',
                ADD COLUMN IF NOT EXISTS slug VARCHAR(255) NULL COMMENT 'URL-friendly product identifier',
                ADD COLUMN IF NOT EXISTS sku VARCHAR(100) NULL COMMENT 'Stock Keeping Unit',
                ADD COLUMN IF NOT EXISTS sale_price DECIMAL(10,2) NULL COMMENT 'Discounted price',
                ADD COLUMN IF NOT EXISTS sale_start_date DATETIME NULL COMMENT 'Sale start date',
                ADD COLUMN IF NOT EXISTS sale_end_date DATETIME NULL COMMENT 'Sale end date',
                ADD COLUMN IF NOT EXISTS meta_title VARCHAR(255) NULL COMMENT 'SEO meta title',
                ADD COLUMN IF NOT EXISTS meta_description TEXT NULL COMMENT 'SEO meta description',
                ADD COLUMN IF NOT EXISTS meta_keywords VARCHAR(500) NULL COMMENT 'SEO keywords'
        """)
        
        # Update status enum to include draft
        print("📝 Updating product status enum...")
        try:
            db.execute_query("""
                ALTER TABLE products
                    MODIFY COLUMN status ENUM('active', 'inactive', 'out_of_stock', 'draft') DEFAULT 'active'
            """)
        except Exception as e:
            logging.warning(f"Status enum update warning (may already exist): {e}")
        
        # Add indexes
        print("📝 Adding product indexes...")
        db.execute_query("""
            ALTER TABLE products
                ADD INDEX IF NOT EXISTS idx_slug (slug),
                ADD INDEX IF NOT EXISTS idx_sku (sku),
                ADD INDEX IF NOT EXISTS idx_low_stock (low_stock_threshold, stock_quantity)
        """)
        
        # 2. Add cost_price to product_variants
        print("📝 Adding cost_price to product_variants...")
        db.execute_query("""
            ALTER TABLE product_variants
                ADD COLUMN IF NOT EXISTS cost_price DECIMAL(10,2) NULL COMMENT 'Cost/purchase price for valuation',
                ADD COLUMN IF NOT EXISTS low_stock_threshold INT DEFAULT 5 COMMENT 'Variant low stock threshold'
        """)
        
        # 3. Create inventory_transactions table
        print("📝 Creating inventory_transactions table...")
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS inventory_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                transaction_type ENUM('sale', 'purchase', 'return', 'adjustment', 'restock') NOT NULL,
                quantity INT NOT NULL,
                previous_stock INT NOT NULL,
                new_stock INT NOT NULL,
                reference_type VARCHAR(50) NULL COMMENT 'order, manual, etc',
                reference_id INT NULL COMMENT 'Related order_id or other ID',
                notes TEXT NULL,
                created_by INT NULL COMMENT 'User ID who performed transaction',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_product (product_id),
                INDEX idx_type (transaction_type),
                INDEX idx_created (created_at),
                INDEX idx_reference (reference_type, reference_id),
                CONSTRAINT fk_inv_trans_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                CONSTRAINT fk_inv_trans_user FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 4. Create low_stock_alerts table
        print("📝 Creating low_stock_alerts table...")
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS low_stock_alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                seller_id INT NOT NULL,
                threshold_quantity INT NOT NULL,
                current_stock INT NOT NULL,
                alert_sent TINYINT(1) DEFAULT 0,
                email_sent_at DATETIME NULL,
                acknowledged TINYINT(1) DEFAULT 0,
                acknowledged_at DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_product_alert (product_id),
                INDEX idx_seller (seller_id),
                INDEX idx_acknowledged (acknowledged),
                INDEX idx_alert_sent (alert_sent),
                CONSTRAINT fk_low_stock_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                CONSTRAINT fk_low_stock_seller FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 5. Create product_images table if not exists
        print("📝 Ensuring product_images table...")
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS product_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                image_url VARCHAR(255) NOT NULL,
                is_primary TINYINT(1) DEFAULT 0,
                display_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_product (product_id),
                CONSTRAINT fk_prod_images_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate()
