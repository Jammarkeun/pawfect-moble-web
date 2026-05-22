# -*- coding: utf-8 -*-
"""
Supabase Connection Test Script

Run this script to verify your Supabase connection is working correctly.

Usage:
    python test_supabase_connection.py
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test Supabase connection"""
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Check environment variables
    print("1. Checking environment variables...")
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url:
        print("   [X] SUPABASE_URL not found in .env")
        return False
    else:
        print(f"   [OK] SUPABASE_URL: {supabase_url[:30]}...")
    
    if not supabase_key:
        print("   [X] SUPABASE_KEY not found in .env")
        return False
    else:
        print(f"   [OK] SUPABASE_KEY: {supabase_key[:30]}...")
    
    print()
    
    # Check if supabase package is installed
    print("2. Checking Supabase package...")
    try:
        from supabase import create_client
        print("   [OK] Supabase package installed")
    except ImportError:
        print("   [X] Supabase package not installed")
        print("   Run: pip install supabase")
        return False
    
    print()
    
    # Try to create client
    print("3. Creating Supabase client...")
    try:
        client = create_client(supabase_url, supabase_key)
        print("   [OK] Supabase client created successfully")
    except Exception as e:
        print(f"   [X] Failed to create client: {e}")
        return False
    
    print()
    
    # Try to query a table (this will fail if tables don't exist yet)
    print("4. Testing database connection...")
    try:
        # Try to query profiles table (Supabase uses 'profiles' instead of 'users')
        response = client.table('profiles').select('id').limit(1).execute()
        print(f"   [OK] Database connection successful")
        print(f"   [OK] Profiles table exists")
        if response.data:
            print(f"   [OK] Found {len(response.data)} profile(s)")
        else:
            print(f"   [i] Profiles table is empty (this is normal for new setup)")
    except Exception as e:
        error_msg = str(e)
        if 'does not exist' in error_msg.lower():
            print("   [!] Tables don't exist yet")
            print("   [i] You need to run the schema SQL in Supabase SQL Editor")
            print("   [i] See SUPABASE_MIGRATION_GUIDE.md for instructions")
        else:
            print(f"   [X] Database query failed: {e}")
            return False
    
    print()
    
    # Test Database service class
    print("5. Testing Database service class...")
    try:
        from app.services.database import Database
        db = Database()
        if db.client:
            print("   [OK] Database service initialized successfully")
        else:
            print("   [X] Database service client is None")
            return False
    except Exception as e:
        print(f"   [X] Failed to initialize Database service: {e}")
        return False
    
    print()
    print("=" * 60)
    print("[OK] CONNECTION TEST PASSED!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. If tables don't exist, run the schema SQL in Supabase SQL Editor")
    print("2. Refactor your model files to use Supabase query builder")
    print("3. Test your application: python app.py")
    print()
    return True


def test_basic_operations():
    """Test basic CRUD operations"""
    print()
    print("=" * 60)
    print("TESTING BASIC OPERATIONS")
    print("=" * 60)
    print()
    
    try:
        from app.services.database import Database
        db = Database()
        
        # Test select
        print("1. Testing SELECT operation...")
        try:
            categories = db.select('categories')
            print(f"   [OK] SELECT works - Found {len(categories)} categories")
        except Exception as e:
            print(f"   [!] SELECT failed: {e}")
        
        print()
        
        # Test insert (we'll try to insert a test category)
        print("2. Testing INSERT operation...")
        try:
            test_category = {
                'name': 'Test Category (DELETE ME)',
                'description': 'This is a test category',
                'is_active': True
            }
            result = db.insert('categories', test_category)
            if result:
                print(f"   [OK] INSERT works - Created category with ID: {result.get('id')}")
                
                # Clean up - delete the test category
                db.delete('categories', filters={'id': result['id']})
                print(f"   [OK] DELETE works - Cleaned up test category")
            else:
                print(f"   [!] INSERT returned no data")
        except Exception as e:
            print(f"   [!] INSERT failed: {e}")
        
        print()
        print("=" * 60)
        print("[OK] BASIC OPERATIONS TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"[X] Failed to test operations: {e}")


if __name__ == '__main__':
    print()
    success = test_connection()
    
    if success:
        # Ask if user wants to test basic operations
        print()
        response = input("Do you want to test basic CRUD operations? (y/n): ")
        if response.lower() == 'y':
            test_basic_operations()
    
    print()
    print("Test complete!")
    print()
