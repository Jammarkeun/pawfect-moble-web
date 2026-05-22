-- Content Management System Tables
-- Run this SQL to create the necessary tables for banners, announcements, and email templates

-- Banners table for homepage banners and promotions
CREATE TABLE IF NOT EXISTS banners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    link_url VARCHAR(500),
    description TEXT,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    target_audience ENUM('all', 'customers', 'sellers', 'riders') DEFAULT 'all',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_active (is_active),
    INDEX idx_display_order (display_order),
    INDEX idx_target_audience (target_audience)
);

-- Announcements table for system-wide notifications
CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'warning', 'success', 'danger') DEFAULT 'info',
    priority ENUM('low', 'normal', 'high', 'urgent') DEFAULT 'normal',
    target_users ENUM('all', 'customers', 'sellers', 'riders', 'admins') DEFAULT 'all',
    start_date DATETIME,
    end_date DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_active (is_active),
    INDEX idx_type (type),
    INDEX idx_priority (priority),
    INDEX idx_target_users (target_users)
);

-- Email templates table for customizable email notifications
CREATE TABLE IF NOT EXISTS email_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    subject VARCHAR(255) NOT NULL,
    html_content TEXT NOT NULL,
    text_content TEXT,
    template_type ENUM('notification', 'marketing', 'system', 'transaction') DEFAULT 'notification',
    variables JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_type (template_type),
    INDEX idx_active (is_active)
);

-- Insert some default email templates
INSERT IGNORE INTO email_templates (name, subject, html_content, text_content, template_type, variables) VALUES
('order_confirmation', 'Order Confirmation - Order #{order_id}',
 '<h2>Order Confirmation</h2>
  <p>Dear {customer_name},</p>
  <p>Thank you for your order! Your order #{order_id} has been successfully placed.</p>
  <p><strong>Order Details:</strong></p>
  <ul>
    <li>Order Number: #{order_id}</li>
    <li>Total Amount: ₱{total_amount}</li>
    <li>Status: {order_status}</li>
  </ul>
  <p>You can track your order status at any time from your account dashboard.</p>
  <p>Best regards,<br>Pawfect Finds Team</p>',
 'Dear {customer_name},\n\nThank you for your order! Your order #{order_id} has been successfully placed.\n\nOrder Details:\n- Order Number: #{order_id}\n- Total Amount: ₱{total_amount}\n- Status: {order_status}\n\nYou can track your order status at any time from your account dashboard.\n\nBest regards,\nPawfect Finds Team',
 'transaction', '{"customer_name": "Customer Name", "order_id": "Order ID", "total_amount": "Total Amount", "order_status": "Order Status"}'),

('order_status_update', 'Order Status Update - Order #{order_id}',
 '<h2>Order Status Update</h2>
  <p>Dear {customer_name},</p>
  <p>Your order #{order_id} status has been updated.</p>
  <p><strong>Status Update:</strong> {old_status} → {new_status}</p>
  <p>You can track your order progress at any time from your account dashboard.</p>
  <p>Best regards,<br>Pawfect Finds Team</p>',
 'Dear {customer_name},\n\nYour order #{order_id} status has been updated.\n\nStatus Update: {old_status} → {new_status}\n\nYou can track your order progress at any time from your account dashboard.\n\nBest regards,\nPawfect Finds Team',
 'notification', '{"customer_name": "Customer Name", "order_id": "Order ID", "old_status": "Old Status", "new_status": "New Status"}'),

('welcome_email', 'Welcome to Pawfect Finds!',
 '<h2>Welcome to Pawfect Finds!</h2>
  <p>Dear {customer_name},</p>
  <p>Welcome to Pawfect Finds! We''re excited to have you join our community of pet lovers.</p>
  <p>Start shopping for your pets today and enjoy:</p>
  <ul>
    <li>Wide variety of pet products</li>
    <li>Multiple seller options</li>
    <li>Fast and reliable delivery</li>
    <li>24/7 customer support</li>
  </ul>
  <p>Best regards,<br>Pawfect Finds Team</p>',
 'Dear {customer_name},\n\nWelcome to Pawfect Finds! We''re excited to have you join our community of pet lovers.\n\nStart shopping for your pets today and enjoy:\n- Wide variety of pet products\n- Multiple seller options\n- Fast and reliable delivery\n- 24/7 customer support\n\nBest regards,\nPawfect Finds Team',
 'marketing', '{"customer_name": "Customer Name"}'),

('seller_approved', 'Congratulations! Your Seller Application Has Been Approved',
 '<h2>Seller Application Approved!</h2>
  <p>Dear {seller_name},</p>
  <p>Congratulations! Your seller application has been approved. You can now start selling on Pawfect Finds.</p>
  <p><strong>Next Steps:</strong></p>
  <ul>
    <li>Log in to your seller dashboard</li>
    <li>Add your first products</li>
    <li>Set up your store profile</li>
    <li>Start receiving orders</li>
  </ul>
  <p>Welcome to the Pawfect Finds seller community!</p>
  <p>Best regards,<br>Pawfect Finds Team</p>',
 'Dear {seller_name},\n\nCongratulations! Your seller application has been approved. You can now start selling on Pawfect Finds.\n\nNext Steps:\n- Log in to your seller dashboard\n- Add your first products\n- Set up your store profile\n- Start receiving orders\n\nWelcome to the Pawfect Finds seller community!\n\nBest regards,\nPawfect Finds Team',
 'notification', '{"seller_name": "Seller Name"}'),

('maintenance_notice', 'Scheduled Maintenance Notice',
 '<h2>Scheduled Maintenance Notice</h2>
  <p>Dear valued customer,</p>
  <p>We will be performing scheduled maintenance on {maintenance_date} from {start_time} to {end_time}.</p>
  <p>During this time, the website may be temporarily unavailable. We apologize for any inconvenience this may cause.</p>
  <p>Thank you for your understanding.</p>
  <p>Best regards,<br>Pawfect Finds Team</p>',
 'Dear valued customer,\n\nWe will be performing scheduled maintenance on {maintenance_date} from {start_time} to {end_time}.\n\nDuring this time, the website may be temporarily unavailable. We apologize for any inconvenience this may cause.\n\nThank you for your understanding.\n\nBest regards,\nPawfect Finds Team',
 'system', '{"maintenance_date": "Maintenance Date", "start_time": "Start Time", "end_time": "End Time"}');