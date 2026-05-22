from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
service_key = os.getenv('SUPABASE_SERVICE_KEY')

client = create_client(url, service_key)

# Check if there's a users table separate from profiles
print("Checking for 'users' table:")
try:
    response = client.table('users').select('*').limit(1).execute()
    if response.data:
        print("  Found 'users' table!")
        print("  Columns:", list(response.data[0].keys()))
        print("  Sample:", response.data[0])
except Exception as e:
    print(f"  No 'users' table: {e}")

# Check auth.users (Supabase's built-in auth)
print("\nChecking Supabase Auth users:")
try:
    # Try to get auth users via RPC or admin API
    response = client.auth.admin.list_users()
    print(f"  Found {len(response)} auth users")
    if response:
        print(f"  Sample user ID: {response[0].id}")
        print(f"  Sample email: {response[0].email}")
except Exception as e:
    print(f"  Cannot access auth users: {e}")
