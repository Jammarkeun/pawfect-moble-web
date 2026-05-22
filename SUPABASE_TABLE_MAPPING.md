# SUPABASE TABLE MAPPING GUIDE

## Your Supabase Schema Uses Different Table Names

Your existing Supabase database uses `profiles` instead of `users`. Here's how to adapt the code:

---

## QUICK FIX - Replace User Model

### Step 1: Backup Current File
```bash
copy app\models\user.py app\models\user_old.py
```

### Step 2: Replace with Supabase Version
```bash
copy app\models\user_supabase.py app\models\user.py
```

This new version uses `profiles` table instead of `users`.

---

## TABLE MAPPING

If your Supabase database has different table names, here's the mapping:

| Old MySQL Table | Supabase Table | Status |
|----------------|----------------|--------|
| `users` | `profiles` | ✅ Confirmed |
| `products` | `products` | ? Check your DB |
| `orders` | `orders` | ✅ Confirmed |
| `categories` | `categories` | ? Check your DB |
| `cart` | `cart` | ? Check your DB |
| `reviews` | `reviews` | ? Check your DB |

---

## HOW TO CHECK YOUR TABLES

### Option 1: Supabase Dashboard
1. Go to your Supabase project
2. Click "Table Editor"
3. See all your tables listed

### Option 2: Python Script
```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Try to query each table
tables = ['profiles', 'products', 'orders', 'categories', 'cart', 'reviews']

for table in tables:
    try:
        response = client.table(table).select('*').limit(1).execute()
        print(f"✓ {table} - EXISTS")
    except Exception as e:
        print(f"✗ {table} - NOT FOUND")
```

---

## UPDATING OTHER MODELS

If you need to update other model files to use different table names:

### Example: Product Model

**If your products table is named differently**, update `app/models/product.py`:

```python
class Product:
    # Change this to match your Supabase table name
    TABLE_NAME = 'products'  # or 'items', 'catalog', etc.
    
    @classmethod
    def get_all(cls):
        db = Database()
        return db.select(cls.TABLE_NAME)
```

---

## FOREIGN KEY REFERENCES

If `profiles` is used instead of `users`, you need to update foreign key references:

### In Orders Table
- Old: `user_id` references `users(id)`
- New: `user_id` references `profiles(id)`

### In Products Table
- Old: `seller_id` references `users(id)`
- New: `seller_id` references `profiles(id)`

**Check your Supabase schema** to see if these are already correct.

---

## TESTING YOUR SETUP

Run this test to verify your tables:

```bash
python test_supabase_connection.py
```

Then test basic operations:

```python
from app.models.user import User

# Test getting a user
user = User.get_by_id(1)
print(f"User: {user}")

# Test getting all users
users = User.get_all_users()
print(f"Total users: {len(users)}")
```

---

## RUNNING YOUR APP

Once you've updated the User model:

```bash
python app.py
```

The app should now work with your Supabase `profiles` table!

---

## COMMON ISSUES

### Issue: "Table 'users' does not exist"
**Solution:** You're still using old code that references `users`. Update to use `profiles`.

### Issue: "Column does not exist"
**Solution:** Your Supabase schema might have different column names. Check your table structure in Supabase dashboard.

### Issue: Foreign key errors
**Solution:** Make sure all foreign keys reference `profiles` instead of `users`.

---

## NEXT STEPS

1. ✅ Replace `app/models/user.py` with the Supabase version
2. ✅ Test the connection: `python test_supabase_connection.py`
3. ✅ Check what other tables you have in Supabase
4. ✅ Update other model files if needed
5. ✅ Run your app: `python app.py`

---

**Your Supabase connection is working! Just need to align the table names.** 🚀
