-- Add variant_id column to order_items table for product variations support
USE pawfect_findsdatabase;

ALTER TABLE order_items ADD COLUMN variant_id INT NULL AFTER seller_id;

-- Add foreign key constraint (optional, as variants can be deleted)
ALTER TABLE order_items ADD CONSTRAINT fk_order_item_variant 
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE SET NULL;

-- Add index for faster queries
CREATE INDEX idx_order_item_variant ON order_items(variant_id);

COMMIT;
