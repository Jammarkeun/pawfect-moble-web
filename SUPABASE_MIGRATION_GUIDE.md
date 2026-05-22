# 🚀 SUPABASE MIGRATION GUIDE

## Overview
This guide will help you migrate your Pawfect Finds application from MySQL to Supabase.

---

## ✅ What Has Been Changed

### 1. **Configuration Files**
- ✅ `config/config.py` - Removed MySQL config, added Supabase config
- ✅ `.env` - Updated with Supabase environment variables
- ✅ `app.py` - Removed SQLAlchemy, using Supabase client
- ✅ `app/__init__.py` - Removed SQLAlchemy dependencies
- ✅ `app/services/database.py` - Complete rewrite for Supabase
- ✅ `app/utils/db.py` - Updated to use Supabase client

### 2. **Dependencies**
- ❌ Removed: `mysql-connector-python`, `Flask-SQLAlchemy`, `Flask-Migrate`
- ✅ Added: `supabase`, `postgrest-py`

---

## 📋 MIGRATION STEPS

### Step 1: Set Up Supabase Project

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com
   - Sign up or log in
   - Click "New Project"

2. **Create Your Project**
   - Choose organization
   - Enter project name: `pawfect-finds`
   - Enter database password (save this!)
   - Select region (closest to you)
   - Click "Create new project"
   - Wait 2-3 minutes for setup

3. **Get Your API Keys**
   - Go to Project Settings (gear icon)
   - Click "API" in sidebar
   - Copy these values:
     - `Project URL` → This is your `SUPABASE_URL`
     - `anon public` key → This is your `SUPABASE_KEY`
     - `service_role` key → This is your `SUPABASE_SERVICE_KEY`

### Step 2: Update Environment Variables

Open your `.env` file and add:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

**Important:** Replace the placeholder values with your actual Supabase credentials!

### Step 3: Create Database Schema in Supabase

1. **Open SQL Editor**
   - In Supabase dashboard, click "SQL Editor"
   - Click "New query"

2. **Run the Schema Creation Script**
   - Copy the SQL from `database/supabase_schema.sql` (see below)
   - Paste into SQL editor
   - Click "Run"

3. **Verify Tables Created**
   - Click "Table Editor" in sidebar
   - You should see all tables: users, products, orders, etc.

### Step 4: Migrate Your Data (If You Have Existing Data)

#### Option A: Export from MySQL and Import to Supabase

1. **Export from MySQL:**
```bash
cd C:\xampp\mysql\bin
mysqldump -u root pawfect_findsdatabase > backup.sql
```

2. **Clean the SQL file:**
   - Remove MySQL-specific syntax
   - Convert AUTO_INCREMENT to SERIAL
   - Convert ENUM to CHECK constraints
   - Convert DATETIME to TIMESTAMP

3. **Import to Supabase:**
   - Use Supabase SQL Editor
   - Paste cleaned SQL
   - Run query

#### Option B: Start Fresh (Recommended for Development)
- Skip data migration
- Let the app create default admin and categories
- Start with clean database

### Step 5: Install New Dependencies

```bash
pip uninstall mysql-connector-python Flask-SQLAlchemy Flask-Migrate
pip install -r requirements-supabase.txt
```

Or install individually:
```bash
pip install supabase==2.3.4
pip install postgrest-py==0.13.2
```

### Step 6: Update Your Code (Model Files)

The database service has been updated, but you need to refactor model files to use Supabase query builder instead of raw SQL.

**Example - Before (MySQL):**
```python
db = Database()
query = "SELECT * FROM users WHERE email = %s"
user = db.execute_query(query, (email,), fetch=True, fetchone=True)
```

**Example - After (Supabase):**
```python
db = Database()
user = db.select_one('users', filters={'email': email})
```

### Step 7: Test the Application

1. **Start the app:**
```bash
python app.py
```

2. **Check for errors:**
   - Look for connection errors
   - Verify Supabase client initialized
   - Test login/signup

3. **Verify database operations:**
   - Create a test user
   - Add a product
   - Place an order

---

## 🔧 SUPABASE SCHEMA SQL

Create this file: `database/supabase_schema.sql`

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'seller', 'admin', 'rider')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'banned')),
    country VARCHAR(100) DEFAULT 'Philippines',
    city VARCHAR(100) DEFAULT 'Manila',
    province VARCHAR(100),
    house_number VARCHAR(50),
    street VARCHAR(150),
    barangay VARCHAR(100),
    postal_code VARCHAR(20),
    id_picture VARCHAR(255),
    profile_image VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    seller_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id BIGINT NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    image_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'out_of_stock')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    seller_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    rider_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    product_total DECIMAL(10,2) DEFAULT 0,
    delivery_fee DECIMAL(10,2) DEFAULT 0,
    admin_commission DECIMAL(10,2) DEFAULT 0,
    seller_earned DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'preparing', 'shipped', 'on_the_way', 'delivered', 'cancelled')),
    shipping_address TEXT NOT NULL,
    payment_method VARCHAR(20) DEFAULT 'cod' CHECK (payment_method IN ('cod', 'online')),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'refunded')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10,2) NOT NULL
);

-- Cart table
CREATE TABLE IF NOT EXISTS cart (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Deliveries table
CREATE TABLE IF NOT EXISTS deliveries (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(id) ON DELETE CASCADE,
    rider_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'assigned' CHECK (status IN ('assigned','picked_up','on_the_way','delivered','failed')),
    delivery_notes TEXT,
    proof_photo_url VARCHAR(255),
    signature_url VARCHAR(255),
    recipient_name VARCHAR(150),
    cod_collected DECIMAL(10,2),
    delivered_lat DECIMAL(10,8),
    delivered_lng DECIMAL(11,8),
    assigned_at TIMESTAMP,
    picked_up_at TIMESTAMP,
    on_the_way_at TIMESTAMP,
    delivered_at TIMESTAMP,
    failed_at TIMESTAMP,
    pod_submitted_at TIMESTAMP,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin','seller','user','rider')),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    related_id BIGINT,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Rider applications table
CREATE TABLE IF NOT EXISTS rider_applications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(20) NOT NULL CHECK (vehicle_type IN ('motorcycle', 'bicycle', 'car', 'scooter')),
    vehicle_plate_number VARCHAR(20),
    vehicle_model VARCHAR(100),
    government_id_path VARCHAR(255),
    vehicle_registration_path VARCHAR(255),
    profile_photo_path VARCHAR(255),
    clearance_path VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    admin_notes TEXT,
    training_completed BOOLEAN DEFAULT FALSE,
    training_completed_at TIMESTAMP,
    submitted_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rider availability table
CREATE TABLE IF NOT EXISTS rider_availability (
    id BIGSERIAL PRIMARY KEY,
    rider_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    is_online BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    last_online TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rider earnings table
CREATE TABLE IF NOT EXISTS rider_earnings (
    id BIGSERIAL PRIMARY KEY,
    rider_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    delivery_id BIGINT NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    base_earning DECIMAL(10,2) DEFAULT 0.00,
    bonus_earning DECIMAL(10,2) DEFAULT 0.00,
    total_earning DECIMAL(10,2) GENERATED ALWAYS AS (base_earning + bonus_earning) STORED,
    created_at TIMESTAMP DEFAULT NOW()
);

-- System settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id BIGSERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Seller requests table
CREATE TABLE IF NOT EXISTS seller_requests (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_name VARCHAR(100) NOT NULL,
    business_description TEXT,
    business_address TEXT NOT NULL,
    business_phone VARCHAR(20) NOT NULL,
    tax_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    admin_notes TEXT,
    requested_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_products_seller ON products(seller_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_seller ON orders(seller_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_notifications_user_role ON notifications(user_id, role, is_read);
CREATE INDEX idx_deliveries_rider ON deliveries(rider_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (basic examples - customize as needed)
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);
```

---

## 🔍 TROUBLESHOOTING

### Error: "Supabase client not initialized"
**Solution:** Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`

### Error: "Table does not exist"
**Solution:** Run the schema SQL in Supabase SQL Editor

### Error: "Permission denied"
**Solution:** Check Row Level Security policies in Supabase dashboard

### Error: "Module 'supabase' not found"
**Solution:** Run `pip install supabase==2.3.4`

---

## 📝 NEXT STEPS

1. **Refactor Model Files**
   - Update `app/models/user.py` to use Supabase methods
   - Update `app/models/product.py` to use Supabase methods
   - Update all other model files

2. **Update Controllers**
   - Replace raw SQL queries with Supabase query builder
   - Use `db.select()`, `db.insert()`, `db.update()`, `db.delete()`

3. **Test Everything**
   - Test user registration and login
   - Test product CRUD operations
   - Test order placement
   - Test rider functionality

4. **Enable Supabase Features**
   - Set up Storage for file uploads
   - Configure Authentication (optional)
   - Set up Realtime subscriptions
   - Configure Row Level Security

---

## 🎯 BENEFITS OF SUPABASE

✅ **No local database setup** - Everything in the cloud
✅ **Built-in authentication** - Can replace custom auth
✅ **Real-time subscriptions** - Live updates without polling
✅ **File storage** - Built-in S3-compatible storage
✅ **Auto-generated APIs** - REST and GraphQL
✅ **Row Level Security** - Database-level security
✅ **Free tier** - 500MB database, 1GB file storage

---

## 📞 SUPPORT

If you encounter issues:
1. Check Supabase logs in dashboard
2. Review this migration guide
3. Check Supabase documentation: https://supabase.com/docs
4. Join Supabase Discord: https://discord.supabase.com

---

**Good luck with your migration! 🚀**
