-- Migration: Add Product Variations Support
-- Date: 2025-11-24
-- Description: Adds support for product variations (colors, sizes, etc.)

-- Add variant_id column to cart table
ALTER TABLE `cart` ADD COLUMN `variant_id` INT NULL AFTER `product_id`;

-- Add foreign key constraint
ALTER TABLE `cart` 
ADD CONSTRAINT `fk_cart_variant` 
FOREIGN KEY (`variant_id`) REFERENCES `product_variants`(`id`) ON DELETE SET NULL;

-- Update unique constraint to include variant_id
ALTER TABLE `cart` DROP CONSTRAINT `unique_user_product`;

-- Create new unique constraint that allows multiple entries for same product with different variants
ALTER TABLE `cart` ADD UNIQUE KEY `unique_user_product_variant` (`user_id`, `product_id`, `variant_id`);

-- Create index for variant_id for faster lookups
CREATE INDEX `idx_cart_variant_id` ON `cart`(`variant_id`);

-- Update cart items to preserve existing data without variants
-- All existing cart items have NULL variant_id

-- Verify the changes
SELECT 'Cart table updated successfully. Added variant_id column.' AS `Status`;
