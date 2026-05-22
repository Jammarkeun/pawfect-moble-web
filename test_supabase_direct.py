#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Supabase connection and check tables"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

print("=" * 60)
print("SUPABASE CONNECTION TEST")
print("=" * 60)
print(f"URL: {SUPABASE_URL}")
print(f"Service Key: {SUPABASE_SERVICE_KEY[:20]}..." if SUPABASE_SERVICE_KEY else "NOT SET")
print()

try:
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("✅ Client created successfully")
    print()
    
    # Test 1: Check categories table
    print("Test 1: Fetching categories...")
    try:
        response = client.table('categories').select('*').limit(5).execute()
        print(f"✅ Categories found: {len(response.data)}")
        if response.data:
            print(f"   Sample: {response.data[0]}")
    except Exception as e:
        print(f"❌ Categories error: {e}")
    print()
    
    # Test 2: Check products table
    print("Test 2: Fetching products...")
    try:
        response = client.table('products').select('*').limit(5).execute()
        print(f"✅ Products found: {len(response.data)}")
        if response.data:
            print(f"   Sample: {response.data[0].get('name', 'N/A')}")
    except Exception as e:
        print(f"❌ Products error: {e}")
    print()
    
    # Test 3: Check profiles table
    print("Test 3: Fetching profiles...")
    try:
        response = client.table('profiles').select('*').limit(5).execute()
        print(f"✅ Profiles found: {len(response.data)}")
    except Exception as e:
        print(f"❌ Profiles error: {e}")
    print()
    
    # Test 4: List all tables (via RPC if available)
    print("Test 4: Checking table structure...")
    try:
        # Try to query information_schema (may fail due to RLS)
        response = client.rpc('get_tables').execute()
        print(f"✅ Tables: {response.data}")
    except Exception as e:
        print(f"⚠️  Cannot list tables (expected): {e}")
    
    print()
    print("=" * 60)
    print("DIAGNOSIS:")
    print("=" * 60)
    print("If you see '❌' errors above, check:")
    print("1. Tables exist in Supabase dashboard")
    print("2. RLS policies allow service_role access")
    print("3. Service key is correct (not anon key)")
    
except Exception as e:
    print(f"❌ FATAL: Cannot connect to Supabase")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
