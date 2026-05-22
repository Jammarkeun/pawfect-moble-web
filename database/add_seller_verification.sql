-- Add verification columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS verification_level ENUM('none', 'basic', 'premium', 'elite') DEFAULT 'none';

-- Update existing sellers with basic verification if they have approved seller_requests
UPDATE users u
JOIN seller_requests sr ON u.id = sr.user_id
SET u.is_verified = TRUE, u.verification_level = 'basic'
WHERE sr.status = 'approved' AND u.role = 'seller';