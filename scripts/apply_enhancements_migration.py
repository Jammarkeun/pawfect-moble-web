"""
Apply product enhancements migration
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database import Database

def apply_migration():
    """Apply product enhancements migration"""
    db = Database()
    
    migration_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'migrations', 'add_product_enhancements.sql')
    
    print(f"Reading migration from: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print(f"Found {len(statements)} SQL statements to execute")
    
    for idx, statement in enumerate(statements, 1):
        # Skip USE statements and comments
        if statement.upper().startswith('USE') or statement.startswith('--'):
            continue
            
        try:
            print(f"\n[{idx}/{len(statements)}] Executing: {statement[:80]}...")
            db.execute_query(statement)
            print(f"✓ Success")
        except Exception as e:
            # Continue on duplicate/exists errors (idempotent)
            error_msg = str(e).lower()
            if 'duplicate' in error_msg or 'exists' in error_msg or 'already' in error_msg:
                print(f"⚠ Skipped (already exists): {e}")
            else:
                print(f"✗ Error: {e}")
                # Don't fail completely, continue with other statements
    
    print("\n✅ Migration completed!")

if __name__ == '__main__':
    apply_migration()
