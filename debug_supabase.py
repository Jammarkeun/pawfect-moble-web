import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

print(f"URL: {url}")
print(f"KEY exists: {bool(key)}")

client = create_client(url, key)

try:
    # Check if profiles table exists and what columns it has
    result = client.table('profiles').select('*').limit(1).execute()
    print(f"\nProfiles table exists!")
    print(f"First row: {result.data}")
    if result.data:
        print(f"Columns: {list(result.data[0].keys())}")
except Exception as e:
    print(f"\nError querying profiles: {e}")
    print(f"Full error: {str(e)}")

# Try to create a simple auth user
try:
    print("\n--- Testing Auth User Creation ---")
    auth_response = client.auth.sign_up({
        'email': 'test123456@example.com',
        'password': 'TestPassword123!'
    })
    print(f"Auth user created: {auth_response.user.id}")
    
    # Now try to insert into profiles with minimal data
    try:
        print("\n--- Testing Minimal Profile Insert ---")
        result = client.table('profiles').insert({
            'id': auth_response.user.id,
            'email': 'test123456@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }).execute()
        print(f"Profile insert successful!")
        print(f"Result: {result.data}")
    except Exception as insert_error:
        print(f"Profile insert failed: {insert_error}")
        
except Exception as e:
    print(f"Auth error: {e}")
