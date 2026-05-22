#!/usr/bin/env python3
"""
Database Migration Script
Adds missing columns to existing tables to match the SQLAlchemy models
"""

import mysql.connector
from mysql.connector import Error
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'pawfect_findsdatabase',
    'user': 'root',
    'password': ''  # You'll need to enter your password
}

def connect_to_database():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(cursor, query, description):
    """Execute a single query with error handling"""
    try:
        cursor.execute(query)
        print(f"✓ {description}")
        return True
    except Error as e:
        if "Duplicate column name" in str(e) or "already exists" in str(e):
            print(f"⚠ {description} (column already exists)")
            return True
        else:
            print(f"✗ Error {description}: {e}")
            return False

def migrate_products_table(cursor):
    """Add missing columns to products table"""
    print("\n=== Migrating Products Table ===")
    
    queries = [
        ("ALTER TABLE products ADD COLUMN sku VARCHAR(50) UNIQUE;", 
         "Added sku column"),
        ("ALTER TABLE products ADD COLUMN weight DECIMAL(8,2);", 
         "Added weight column"),
        ("ALTER TABLE products ADD COLUMN dimensions VARCHAR(50);", 
         "Added dimensions column"),
        ("ALTER TABLE products ADD COLUMN brand VARCHAR(100);", 
         "Added brand column"),
        ("ALTER TABLE products ADD COLUMN age_group ENUM('puppy', 'adult', 'senior', 'all_ages') DEFAULT 'all_ages';", 
         "Added age_group column"),
        ("ALTER TABLE products ADD COLUMN pet_type ENUM('dog', 'cat', 'fish', 'bird', 'other') NOT NULL DEFAULT 'dog';", 
         "Added pet_type column"),
        ("ALTER TABLE products ADD COLUMN featured BOOLEAN DEFAULT FALSE;", 
         "Added featured column"),
    ]
    
    for query, description in queries:
        execute_query(cursor, query, description)

def migrate_users_table(cursor):
    """Add missing columns to users table"""
    print("\n=== Migrating Users Table ===")

    queries = [
        ("ALTER TABLE users ADD COLUMN role ENUM('user', 'seller', 'admin', 'rider') DEFAULT 'user';",
         "Added role column"),
        ("ALTER TABLE users ADD COLUMN status ENUM('active', 'inactive', 'banned') DEFAULT 'active';",
         "Added status column"),
        ("ALTER TABLE users ADD COLUMN country VARCHAR(100) NOT NULL DEFAULT 'Philippines';",
         "Added country column"),
        ("ALTER TABLE users ADD COLUMN city VARCHAR(100) NOT NULL DEFAULT 'Manila';",
         "Added city column"),
        ("ALTER TABLE users ADD COLUMN id_picture VARCHAR(255);",
         "Added id_picture column"),
        ("ALTER TABLE users ADD COLUMN profile_image VARCHAR(255);",
         "Added profile_image column"),
        ("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
         "Added created_at column"),
        ("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;",
         "Added updated_at column"),
        ("ALTER TABLE users MODIFY COLUMN address TEXT NOT NULL;",
         "Made address column required"),
    ]

    for query, description in queries:
        execute_query(cursor, query, description)

    # Update existing image paths to include /static/ prefix
    print("\nUpdating existing image paths...")
    update_products_query = """
    UPDATE products
    SET image_url = CONCAT('/static/uploads/products/', image_url)
    WHERE image_url IS NOT NULL AND image_url NOT LIKE '/static/%'
    """
    execute_query(cursor, update_products_query, "Updated product image paths")

    update_profiles_query = """
    UPDATE users
    SET profile_image = CONCAT('/static/uploads/profiles/', profile_image)
    WHERE profile_image IS NOT NULL AND profile_image NOT LIKE '/static/%'
    """
    execute_query(cursor, update_profiles_query, "Updated profile image paths")

def create_missing_tables(cursor):
    """Create tables that might be missing"""
    print("\n=== Creating Missing Tables ===")

    # Add business_permit column to seller_requests table
    alter_seller_requests_query = """
    ALTER TABLE seller_requests ADD COLUMN IF NOT EXISTS business_permit VARCHAR(255) NULL AFTER tax_id;
    """
    execute_query(cursor, alter_seller_requests_query, "Added business_permit column to seller_requests table")

    # Create seller_applications table if it doesn't exist
    seller_applications_query = """
    CREATE TABLE IF NOT EXISTS seller_applications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        business_name VARCHAR(200) NOT NULL,
        business_description TEXT,
        business_address TEXT NOT NULL,
        tax_id VARCHAR(50),
        phone VARCHAR(20) NOT NULL,
        email VARCHAR(100) NOT NULL,
        documents TEXT,
        status ENUM('pending', 'approved', 'rejected', 'under_review') DEFAULT 'pending',
        admin_notes TEXT,
        reviewed_by INT,
        reviewed_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (reviewed_by) REFERENCES users(id)
    );
    """
    execute_query(cursor, seller_applications_query, "Created seller_applications table")

    # Create notifications table if it doesn't exist
    notifications_query = """
    CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        type ENUM('order_status', 'seller_application', 'product_review', 'delivery_update', 'general') NOT NULL,
        title VARCHAR(200) NOT NULL,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        related_id INT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    execute_query(cursor, notifications_query, "Created notifications table")

    # Create rider_performance table if it doesn't exist
    rider_performance_query = """
    CREATE TABLE IF NOT EXISTS rider_performance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        rider_id INT NOT NULL,
        order_id INT NOT NULL,
        rating INT,
        feedback TEXT,
        delivery_time_minutes INT,
        rated_by INT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (rider_id) REFERENCES users(id),
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (rated_by) REFERENCES users(id),
        CONSTRAINT performance_rating_range CHECK (rating >= 1 AND rating <= 5)
    );
    """
    execute_query(cursor, rider_performance_query, "Created rider_performance table")

    # Create rider_earnings table if it doesn't exist
    rider_earnings_query = """
    CREATE TABLE IF NOT EXISTS rider_earnings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        rider_id INT NOT NULL,
        order_id INT NOT NULL,
        base_fee DECIMAL(8,2) NOT NULL,
        distance_fee DECIMAL(8,2) DEFAULT 0,
        tip_amount DECIMAL(8,2) DEFAULT 0,
        total_earning DECIMAL(8,2) NOT NULL,
        status ENUM('pending', 'paid') DEFAULT 'pending',
        paid_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (rider_id) REFERENCES users(id),
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    """
    execute_query(cursor, rider_earnings_query, "Created rider_earnings table")

    # Create website_settings table if it doesn't exist
    website_settings_query = """
    CREATE TABLE IF NOT EXISTS website_settings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        setting_key VARCHAR(100) UNIQUE NOT NULL,
        setting_value TEXT,
        description TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    execute_query(cursor, website_settings_query, "Created website_settings table")

    # Create wishlist table if it doesn't exist
    wishlist_query = """
    CREATE TABLE IF NOT EXISTS wishlist (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id),
        UNIQUE KEY unique_user_product_wish (user_id, product_id)
    );
    """
    execute_query(cursor, wishlist_query, "Created wishlist table")

    # Create system_logs table if it doesn't exist
    system_logs_query = """
    CREATE TABLE IF NOT EXISTS system_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        action VARCHAR(100) NOT NULL,
        details TEXT,
        ip_address VARCHAR(45),
        user_agent TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    execute_query(cursor, system_logs_query, "Created system_logs table")

def migrate_orders_table(cursor):
    """Add missing columns to orders table"""
    print("\n=== Migrating Orders Table ===")
    
    queries = [
        ("ALTER TABLE orders ADD COLUMN rider_id INT;", 
         "Added rider_id column"),
        ("ALTER TABLE orders ADD COLUMN delivered_at DATETIME;", 
         "Added delivered_at column"),
        ("ALTER TABLE orders ADD FOREIGN KEY (rider_id) REFERENCES users(id);", 
         "Added rider_id foreign key"),
    ]
    
    for query, description in queries:
        execute_query(cursor, query, description)

def main():
    """Main migration function"""
    print("=== Pawfect Finds Database Migration ===")
    
    # Get password from user
    db_password = input("Enter your MySQL root password (or press Enter if no password): ").strip()
    DB_CONFIG['password'] = db_password
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to database. Exiting.")
        sys.exit(1)
    
    try:
        cursor = connection.cursor()
        
        # Run migrations
        migrate_users_table(cursor)
        migrate_products_table(cursor)
        migrate_orders_table(cursor)
        create_missing_tables(cursor)
        
        # Commit changes
        connection.commit()
        print("\n=== Migration Completed Successfully! ===")
        
    except Error as e:
        print(f"Error during migration: {e}")
        connection.rollback()
        sys.exit(1)
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()