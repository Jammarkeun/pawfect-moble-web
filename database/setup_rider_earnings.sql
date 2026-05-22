-- Rider Earnings System Database Setup
-- Run this script to set up or update the database tables for the rider earnings system

-- Create payout_requests table if it doesn't exist
CREATE TABLE IF NOT EXISTS payout_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rider_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payout_method VARCHAR(50) NOT NULL,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME NULL,
    paid_at DATETIME NULL,
    admin_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rider_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_rider_id (rider_id),
    INDEX idx_status (status),
    INDEX idx_requested_at (requested_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add payout method columns to users table if they don't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS payout_method VARCHAR(50) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bank_name VARCHAR(100) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS account_number VARCHAR(50) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS account_name VARCHAR(100) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS gcash_number VARCHAR(20) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS gcash_name VARCHAR(100) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS pickup_location VARCHAR(100) NULL;

-- Ensure rider_earnings table has all required columns
ALTER TABLE rider_earnings ADD COLUMN IF NOT EXISTS status ENUM('pending', 'paid') DEFAULT 'pending';
ALTER TABLE rider_earnings ADD COLUMN IF NOT EXISTS paid_at DATETIME NULL;

-- Create index for faster queries
ALTER TABLE rider_earnings ADD INDEX IF NOT EXISTS idx_rider_status (rider_id, status);
ALTER TABLE rider_earnings ADD INDEX IF NOT EXISTS idx_created_at (created_at);

-- Verify website_settings has rider_base_fee
INSERT IGNORE INTO website_settings (setting_key, setting_value, description)
VALUES ('rider_base_fee', '50.00', 'Base delivery fee for riders in PHP');

-- Display results
SELECT 'Payout system setup complete!' as status;
SELECT COUNT(*) as total_payout_requests FROM payout_requests;
SELECT COUNT(*) as total_earnings FROM rider_earnings;
