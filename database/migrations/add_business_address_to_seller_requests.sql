-- Migration: Add business_address column to seller_requests table
-- This fixes the PGRST204 error when trying to insert seller requests

-- Add business_address column if it doesn't exist
ALTER TABLE seller_requests
ADD COLUMN IF NOT EXISTS business_address TEXT;

-- Update existing records to have a placeholder if null
UPDATE seller_requests 
SET business_address = '' 
WHERE business_address IS NULL;

-- Create an index on business_address for better query performance
CREATE INDEX IF NOT EXISTS idx_seller_requests_business_address 
ON seller_requests(business_address);
