# 🚀 SUPABASE QUICK REFERENCE

## Environment Variables (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

---

## Basic Operations

### Initialize Database
```python
from app.services.database import Database

db = Database()
```

### SELECT - Get All Records
```python
# Get all users
users = db.select('users')

# Get with specific columns
users = db.select('users', columns='id, email, username')

# Get with filters
active_users = db.select('users', filters={'status': 'active'})
```

### SELECT - Get One Record
```python
# Get single user by email
user = db.select_one('users', filters={'email': 'user@example.com'})

# Get by ID
user = db.select_one('users', filters={'id': 123})
```

### INSERT - Create Record
```python
# Insert new user
new_user = db.insert('users', {
    'username': 'john_doe',
    'email': 'john@example.com',
    'password_hash': hashed_password,
    'first_name': 'John',
    'last_name': 'Doe',
    'role': 'user'
})

# Returns the inserted record with ID
print(new_user['id'])
```

### UPDATE - Modify Record
```python
# Update user by ID
updated = db.update(
    'users',
    data={'first_name': 'Jane', 'last_name': 'Smith'},
    filters={'id': 123}
)

# Update multiple records
db.update(
    'products',
    data={'status': 'inactive'},
    filters={'seller_id': 456}
)
```

### DELETE - Remove Record
```python
# Delete by ID
db.delete('users', filters={'id': 123})

# Delete with conditions
db.delete('cart', filters={'user_id': 456, 'product_id': 789})
```

---

## Advanced Queries

### Using Supabase Client Directly
```python
from app.services.database import Database

db = Database()
client = db.client

# Complex query with multiple filters
response = client.table('products') \
    .select('*') \
    .eq('status', 'active') \
    .gte('price', 100) \
    .lte('price', 500) \
    .order('created_at', desc=True) \
    .limit(10) \
    .execute()

products = response.data
```

### Joins
```python
# Get orders with user info
response = client.table('orders') \
    .select('*, users(username, email)') \
    .eq('status', 'pending') \
    .execute()

orders = response.data
```

### Count Records
```python
response = client.table('products') \
    .select('*', count='exact') \
    .eq('seller_id', 123) \
    .execute()

count = response.count
```

### Search
```python
# Text search
response = client.table('products') \
    .select('*') \
    .ilike('name', '%dog food%') \
    .execute()

products = response.data
```

---

## RPC (Remote Procedure Calls)

### Call Database Function
```python
# Call custom function
result = db.rpc('calculate_seller_earnings', {
    'seller_id': 123,
    'start_date': '2024-01-01',
    'end_date': '2024-12-31'
})
```

---

## File Storage (Supabase Storage)

### Upload File
```python
from supabase import create_client
import os

client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Upload file
with open('product.jpg', 'rb') as f:
    response = client.storage.from_('products').upload(
        'product_123.jpg',
        f,
        {'content-type': 'image/jpeg'}
    )

# Get public URL
url = client.storage.from_('products').get_public_url('product_123.jpg')
```

### Download File
```python
# Download file
response = client.storage.from_('products').download('product_123.jpg')
```

### Delete File
```python
# Delete file
response = client.storage.from_('products').remove(['product_123.jpg'])
```

---

## Real-time Subscriptions

### Listen to Changes
```python
from supabase import create_client
import os

client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def handle_order_change(payload):
    print(f"Order changed: {payload}")

# Subscribe to orders table
subscription = client.table('orders') \
    .on('INSERT', handle_order_change) \
    .subscribe()
```

---

## Common Patterns

### User Authentication
```python
def authenticate_user(email, password):
    from werkzeug.security import check_password_hash
    
    db = Database()
    user = db.select_one('users', filters={'email': email})
    
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None
```

### Create User
```python
def create_user(username, email, password, **kwargs):
    from werkzeug.security import generate_password_hash
    
    db = Database()
    
    # Check if exists
    existing = db.select_one('users', filters={'email': email})
    if existing:
        return None
    
    # Create user
    user_data = {
        'username': username,
        'email': email,
        'password_hash': generate_password_hash(password),
        'role': 'user',
        'status': 'active',
        **kwargs
    }
    
    return db.insert('users', user_data)
```

### Get User Orders
```python
def get_user_orders(user_id):
    db = Database()
    return db.select('orders', filters={'user_id': user_id})
```

### Update Product Stock
```python
def update_stock(product_id, quantity):
    db = Database()
    
    # Get current stock
    product = db.select_one('products', filters={'id': product_id})
    if not product:
        return False
    
    new_stock = product['stock_quantity'] + quantity
    
    # Update
    db.update(
        'products',
        data={'stock_quantity': new_stock},
        filters={'id': product_id}
    )
    return True
```

---

## Error Handling

```python
try:
    db = Database()
    user = db.select_one('users', filters={'id': 123})
    if not user:
        print("User not found")
except Exception as e:
    print(f"Database error: {e}")
```

---

## Migration from MySQL

### Before (MySQL)
```python
db = Database()
query = "SELECT * FROM users WHERE email = %s"
user = db.execute_query(query, (email,), fetch=True, fetchone=True)
```

### After (Supabase)
```python
db = Database()
user = db.select_one('users', filters={'email': email})
```

---

## Tips & Best Practices

1. **Use filters parameter** for simple queries
2. **Use client directly** for complex queries
3. **Enable RLS** for security
4. **Use indexes** for performance
5. **Batch operations** when possible
6. **Handle errors** gracefully
7. **Use environment variables** for credentials
8. **Test queries** in Supabase dashboard first

---

## Useful Links

- Supabase Docs: https://supabase.com/docs
- Python Client: https://supabase.com/docs/reference/python
- SQL Editor: https://app.supabase.com (in your project)
- Storage: https://supabase.com/docs/guides/storage

---

**Happy coding! 🎉**
