-- Migration: Add multi-participant chat support
-- This allows conversations between: customer-seller, seller-admin, seller-rider, customer-rider

-- Add new columns to chat_rooms table
ALTER TABLE chat_rooms 
ADD COLUMN participant1_id INT NULL AFTER user_id,
ADD COLUMN participant2_id INT NULL AFTER participant1_id,
ADD COLUMN conversation_type ENUM('customer_admin', 'customer_seller', 'seller_admin', 'seller_rider', 'customer_rider') DEFAULT 'customer_admin' AFTER participant2_id,
ADD COLUMN related_order_id INT NULL AFTER conversation_type,
ADD INDEX idx_participants (participant1_id, participant2_id),
ADD INDEX idx_conversation_type (conversation_type),
ADD INDEX idx_related_order (related_order_id),
ADD FOREIGN KEY (participant1_id) REFERENCES users(id) ON DELETE CASCADE,
ADD FOREIGN KEY (participant2_id) REFERENCES users(id) ON DELETE CASCADE,
ADD FOREIGN KEY (related_order_id) REFERENCES orders(id) ON DELETE SET NULL;

-- Migrate existing data: set participant1_id = user_id for existing rooms
UPDATE chat_rooms SET participant1_id = user_id WHERE participant1_id IS NULL;

-- Update chat_messages to remove is_support flag (we'll use conversation_type instead)
-- Keep is_support for backward compatibility but add sender_role
ALTER TABLE chat_messages
ADD COLUMN sender_role ENUM('customer', 'seller', 'admin', 'rider') NULL AFTER user_id;

-- Update existing messages to set sender_role based on user role
UPDATE chat_messages cm
JOIN users u ON cm.user_id = u.id
SET cm.sender_role = 
    CASE 
        WHEN u.role = 'user' THEN 'customer'
        WHEN u.role = 'seller' THEN 'seller'
        WHEN u.role = 'admin' THEN 'admin'
        WHEN u.role = 'rider' THEN 'rider'
        ELSE 'customer'
    END
WHERE cm.sender_role IS NULL;

