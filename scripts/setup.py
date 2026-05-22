#!/usr/bin/env python3
"""
Setup script for Pawfect Finds E-commerce Platform
This script helps initialize the project by:
1. Installing Python dependencies
2. Setting up the database
3. Creating default admin user and categories
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("🐾 Pawfect Finds E-commerce Platform Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the project root directory (where app.py is located)")
        sys.exit(1)
    
    print("\n📋 Setup Checklist:")
    print("1. Install Python dependencies")
    print("2. Initialize Flask application")
    print("3. Create database tables")
    print("4. Setup default data (categories, admin user)")
    
    # Install dependencies
    print("\n" + "=" * 40)
    print("STEP 1: Installing Dependencies")
    print("=" * 40)
    
    if not run_command("pip install -r requirements.txt", 
                      "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your Python/pip installation.")
        sys.exit(1)
    
    # Initialize the application
    print("\n" + "=" * 40)
    print("STEP 2: Database Initialization")
    print("=" * 40)
    
    print("\n📌 IMPORTANT: Before proceeding, make sure:")
    print("   - XAMPP is running")
    print("   - MySQL service is started")
    print("   - MySQL is accessible on localhost:3306")
    
    proceed = input("\nAre you ready to proceed? (y/N): ").lower().strip()
    if proceed != 'y':
        print("Setup cancelled. Please ensure MySQL is running and try again.")
        sys.exit(0)
    
    # Test database connection and create tables
    print("\n🗄️  Testing database connection and creating tables...")
    
    try:
        # Import and initialize the database
        from app.services.database import Database
        db = Database()
        
        print("✓ Database connection successful")
        
        # Create tables
        print("Creating database tables...")
        db.create_tables()
        print("✓ Database tables created successfully")
        print("✓ Default categories inserted")
        print("✓ Default admin user created")
        
    except ImportError as e:
        print(f"❌ Failed to import modules: {e}")
        print("Make sure all dependencies are installed correctly.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\nPossible solutions:")
        print("- Check if XAMPP MySQL is running")
        print("- Verify MySQL credentials in config/config.py")
        print("- Ensure MySQL is accessible on localhost:3306")
        sys.exit(1)
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    
    print("\n📋 What's been set up:")
    print("✓ Python dependencies installed")
    print("✓ Database 'pawfect_finds' created")
    print("✓ All necessary tables created")
    print("✓ 6 default pet categories added")
    print("✓ Default admin account created")
    
    print("\n🔑 Default Admin Account:")
    print("   Email: admin@pawfectfinds.com")
    print("   Password: admin123")
    
    print("\n🚀 Next Steps:")
    print("1. Start the Flask application:")
    print("   python app.py")
    print("\n2. Open your browser and go to:")
    print("   http://localhost:5000")
    print("\n3. Login with the admin account to manage the system")
    print("   or create a regular user account to test the customer flow")
    
    print("\n📁 Project Structure:")
    print("   app.py              - Main Flask application")
    print("   config/             - Configuration files")
    print("   app/models/         - Database models")
    print("   app/controllers/    - Route controllers")
    print("   templates/          - HTML templates")
    print("   static/             - CSS, JS, images")
    
    print("\n💡 Tips:")
    print("- Test the seller request flow by creating a user account")
    print("- Apply to become a seller and approve it via admin panel")
    print("- Add products as a seller and test the shopping flow")
    print("- Check the admin analytics and management features")
    
    print(f"\nHappy coding! 🐾")

if __name__ == "__main__":
    main()
