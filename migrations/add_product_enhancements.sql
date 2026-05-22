-- ====================================================
-- PRODUCT ENHANCEMENTS MIGRATION
-- Adds support for: variants, bundles, scheduled pricing, SEO, drafts
-- ====================================================

USE pawfect_findsdatabase;

-- 1. ADD SEO FIELDS TO PRODUCTS
ALTER TABLE products 
    ADD COLUMN IF NOT EXISTS meta_title VARCHAR(200) NULL AFTER description,
    ADD COLUMN IF NOT EXISTS meta_description TEXT NULL AFTER meta_title,
    ADD COLUMN IF NOT EXISTS meta_keywords VARCHAR(255) NULL AFTER meta_description,
    ADD COLUMN IF NOT EXISTS slug VARCHAR(255) NULL AFTER name,
    ADD INDEX IF NOT EXISTS idx_slug (slug);

-- 2. ADD SCHEDULED PRICING FIELDS
ALTER TABLE products
    ADD COLUMN IF NOT EXISTS sale_price DECIMAL(10,2) NULL AFTER price,
    ADD COLUMN IF NOT EXISTS sale_start_date DATETIME NULL AFTER sale_price,
    ADD COLUMN IF NOT EXISTS sale_end_date DATETIME NULL AFTER sale_start_date,
    ADD INDEX IF NOT EXISTS idx_sale_dates (sale_start_date, sale_end_date);

-- 3. EXTEND STATUS ENUM TO SUPPORT DRAFT
ALTER TABLE products MODIFY COLUMN status ENUM('active', 'inactive', 'out_of_stock', 'draft') DEFAULT 'active';

-- 4. ADD SKU IF NOT EXISTS (for variants)
ALTER TABLE products 
    ADD COLUMN IF NOT EXISTS sku VARCHAR(100) NULL AFTER name,
    ADD UNIQUE INDEX IF NOT EXISTS idx_sku (sku);

-- ====================================================
-- PRODUCT VARIANTS TABLE
-- ====================================================
CREATE TABLE IF NOT EXISTS product_variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    name VARCHAR(100) NOT NULL COMMENT 'Variant name e.g. "Red - Large"',
    sku VARCHAR(100) NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    sale_price DECIMAL(10,2) NULL,
    stock_quantity INT DEFAULT 0,
    image_url VARCHAR(255) NULL,
    attributes JSON NULL COMMENT 'e.g. {"color":"Red","size":"Large"}',
    display_order INT DEFAULT 0,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_id (product_id),
    INDEX idx_status (status),
    INDEX idx_sku_variant (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================
-- PRODUCT BUNDLES TABLE
-- ====================================================
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

-- ====================================================
-- BUNDLE ITEMS TABLE (many-to-many: bundles <-> products)
-- ====================================================
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

-- ====================================================
-- PRODUCT CATEGORIES ENHANCEMENT (ensure exists)
-- ====================================================
-- Already exists, but ensure filter-friendly indexes
ALTER TABLE products ADD INDEX IF NOT EXISTS idx_category_status (category_id, status);
ALTER TABLE products ADD INDEX IF NOT EXISTS idx_seller_category (seller_id, category_id);

-- ====================================================
-- UPDATE DISPLAY ORDER FOR PRODUCT IMAGES
-- ====================================================
ALTER TABLE product_images 
    ADD COLUMN IF NOT EXISTS display_order INT DEFAULT 0 AFTER is_primary,
    ADD INDEX IF NOT EXISTS idx_display_order (product_id, display_order);
