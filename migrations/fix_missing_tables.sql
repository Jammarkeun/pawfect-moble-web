USE pawfect_findsdatabase;

-- Create product_variants table
CREATE TABLE IF NOT EXISTS product_variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    sku VARCHAR(100) NULL,
    price DECIMAL(10,2) NOT NULL,
    sale_price DECIMAL(10,2) NULL,
    stock_quantity INT DEFAULT 0,
    image_url VARCHAR(255) NULL,
    attributes JSON NULL,
    display_order INT DEFAULT 0,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_id (product_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create unique index on sku if it doesn't exist
CREATE UNIQUE INDEX idx_sku_variant ON product_variants(sku);

-- Create product_bundles table
CREATE TABLE IF NOT EXISTS product_bundles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    bundle_price DECIMAL(10,2) NOT NULL,
    discount_percentage DECIMAL(5,2) NULL,
    image_url VARCHAR(255) NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_seller_id (seller_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create bundle_items table
CREATE TABLE IF NOT EXISTS bundle_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bundle_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT NULL,
    quantity INT DEFAULT 1,
    display_order INT DEFAULT 0,
    FOREIGN KEY (bundle_id) REFERENCES product_bundles(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE SET NULL,
    INDEX idx_bundle_id (bundle_id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add columns to products table
ALTER TABLE products 
    ADD COLUMN IF NOT EXISTS meta_title VARCHAR(200) NULL,
    ADD COLUMN IF NOT EXISTS meta_description TEXT NULL,
    ADD COLUMN IF NOT EXISTS meta_keywords VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS slug VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS sale_price DECIMAL(10,2) NULL,
    ADD COLUMN IF NOT EXISTS sale_start_date DATETIME NULL,
    ADD COLUMN IF NOT EXISTS sale_end_date DATETIME NULL,
    ADD COLUMN IF NOT EXISTS sku VARCHAR(100) NULL;

-- Modify status enum to include draft
ALTER TABLE products MODIFY COLUMN status ENUM('active', 'inactive', 'out_of_stock', 'draft') DEFAULT 'active';

-- Add indexes
ALTER TABLE products ADD INDEX IF NOT EXISTS idx_slug (slug);
ALTER TABLE products ADD INDEX IF NOT EXISTS idx_sale_dates (sale_start_date, sale_end_date);
ALTER TABLE products ADD INDEX IF NOT EXISTS idx_category_status (category_id, status);
ALTER TABLE products ADD INDEX IF NOT EXISTS idx_seller_category (seller_id, category_id);

-- Add unique constraint on sku if not exists
ALTER TABLE products ADD UNIQUE INDEX IF NOT EXISTS idx_sku (sku);
