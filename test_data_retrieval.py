from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

client = create_client(url, key)

print("=== TESTING DATA RETRIEVAL ===\n")

# Test categories
print("1. Categories:")
try:
    response = client.table('categories').select('*').execute()
    print(f"   Found {len(response.data)} categories")
    for cat in response.data:
        print(f"   - {cat}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n2. Products:")
try:
    response = client.table('products').select('*').execute()
    print(f"   Found {len(response.data)} products")
    for prod in response.data[:3]:  # Show first 3
        print(f"   - {prod}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n3. Profiles:")
try:
    response = client.table('profiles').select('*').execute()
    print(f"   Found {len(response.data)} profiles")
    for prof in response.data[:3]:  # Show first 3
        print(f"   - {prof}")
except Exception as e:
    print(f"   ERROR: {e}")
