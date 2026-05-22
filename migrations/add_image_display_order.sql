-- Add display_order column to product_images table
ALTER TABLE product_images ADD COLUMN display_order INT DEFAULT 0;

-- Create index for sorting
CREATE INDEX idx_product_images_display_order ON product_images(product_id, display_order);
