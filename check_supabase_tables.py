from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
service_key = os.getenv('SUPABASE_SERVICE_KEY')

print("=== CHECKING SUPABASE SETUP ===\n")

# Try with anon key first
print("1. Testing with ANON key:")
client = create_client(url, key)
try:
    response = client.table('categories').select('*').execute()
    print(f"   Categories: {len(response.data)} rows")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    response = client.table('products').select('*').execute()
    print(f"   Products: {len(response.data)} rows")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    response = client.table('profiles').select('*').execute()
    print(f"   Profiles: {len(response.data)} rows")
except Exception as e:
    print(f"   ERROR: {e}")

# Try with service key (bypasses RLS)
print("\n2. Testing with SERVICE_ROLE key (bypasses RLS):")
client_service = create_client(url, service_key)
try:
    response = client_service.table('categories').select('*').execute()
    print(f"   Categories: {len(response.data)} rows")
    if response.data:
        print(f"   Sample: {response.data[0]}")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    response = client_service.table('products').select('*').execute()
    print(f"   Products: {len(response.data)} rows")
    if response.data:
        print(f"   Sample: {response.data[0]}")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    response = client_service.table('profiles').select('*').execute()
    print(f"   Profiles: {len(response.data)} rows")
    if response.data:
        print(f"   Sample: {response.data[0]}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n=== DIAGNOSIS ===")
print("If SERVICE_ROLE key shows data but ANON key doesn't:")
print("  → RLS (Row Level Security) is blocking access")
print("  → Go to Supabase Dashboard → Authentication → Policies")
print("  → Add policies to allow public read access")
print("\nIf both show 0 rows:")
print("  → Tables are empty, you need to insert data")
