#!/usr/bin/env python3
"""Check if environment variables are set correctly"""
import os

print("\n" + "="*60)
print("ENVIRONMENT VARIABLES CHECK")
print("="*60)

required_vars = {
    'SUPABASE_URL': 'https://pplprkapzevcuelsqcfv.supabase.co',
    'SUPABASE_SERVICE_KEY': 'eyJhbGci...(your service key)',
}

for var_name, expected in required_vars.items():
    value = os.getenv(var_name)
    if value:
        # Mask the key for security
        if 'KEY' in var_name:
            display = value[:20] + '...' if len(value) > 20 else value
        else:
            display = value
        print(f"✅ {var_name}: {display}")
    else:
        print(f"❌ {var_name}: NOT SET")
        print(f"   Expected: {expected}")

print("="*60)

# Try to initialize Supabase
print("\nTrying to initialize Supabase client...")
try:
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if url and key:
        client = create_client(url, key)
        print("✅ Supabase client initialized successfully!")
        
        # Try a simple query
        response = client.table('categories').select('*').limit(1).execute()
        print(f"✅ Database connection works! Found {len(response.data)} categories")
    else:
        print("❌ Cannot initialize - environment variables missing")
except Exception as e:
    print(f"❌ Error: {e}")

print("="*60 + "\n")
