"""
Apply Enhanced Features Database Migrations
This script applies all the new database tables and enhancements.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database import Database


def run_migration():
    """Apply all database migrations"""
    db = Database()
    
    print("\n" + "="*60)
    print("PAWFECTFINDS - ENHANCED FEATURES MIGRATION")
    print("="*60 + "\n")
    
    # Read the SQL file
    sql_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'database', 'enhanced_features_schema.sql')
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("✓ SQL file loaded successfully\n")
        
        # Split into individual statements (excluding DELIMITER statements)
        statements = []
        current_statement = []
        delimiter = ';'
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Handle DELIMITER changes
            if line.startswith('DELIMITER'):
                if '$$' in line:
                    delimiter = '$$'
                else:
                    delimiter = ';'
                continue
            
            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue
            
            # Remove inline comments (-- comment)
            if '--' in line:
                line = line.split('--')[0].strip()
            
            # Skip if line became empty after removing comment
            if not line:
                continue
            
            current_statement.append(line)
            
            # End of statement detection
            if line.endswith(delimiter):
                # Remove the delimiter from the end
                statement_text = ' '.join(current_statement)
                if delimiter == '$$':
                    statement_text = statement_text[:-2].strip()  # Remove $$
                else:
                    statement_text = statement_text[:-1].strip()  # Remove ;
                
                if statement_text:
                    statements.append(statement_text)
                current_statement = []
        
        # Execute each statement
        total = len(statements)
        success_count = 0
        error_count = 0
        
        print(f"Executing {total} SQL statements...\n")
        
        for i, statement in enumerate(statements, 1):
            if not statement.strip():
                continue
            
            try:
                # Determine statement type for logging
                statement_upper = statement.upper()
                statement_type = "UNKNOWN"
                
                if statement_upper.startswith('CREATE TABLE'):
                    words = statement.split()
                    # Find table name after 'IF NOT EXISTS' or directly after 'TABLE'
                    try:
                        if 'IF' in statement_upper and 'NOT' in statement_upper:
                            table_name = words[5] if len(words) > 5 else "unknown"
                        else:
                            table_name = words[2] if len(words) > 2 else "unknown"
                    except:
                        table_name = "unknown"
                    statement_type = f"CREATE TABLE {table_name}"
                elif statement_upper.startswith('ALTER TABLE'):
                    words = statement.split()
                    table_name = words[2] if len(words) > 2 else "unknown"
                    statement_type = f"ALTER TABLE {table_name}"
                elif statement_upper.startswith('CREATE TRIGGER'):
                    words = statement.split()
                    # Find trigger name after 'IF NOT EXISTS' or directly after 'TRIGGER'
                    try:
                        if 'IF' in statement_upper and 'NOT' in statement_upper:
                            trigger_name = words[5] if len(words) > 5 else "unknown"
                        else:
                            trigger_name = words[2] if len(words) > 2 else "unknown"
                    except:
                        trigger_name = "unknown"
                    statement_type = f"CREATE TRIGGER {trigger_name}"
                
                db.execute_query(statement)
                print(f"  [{i}/{total}] ✓ {statement_type}")
                success_count += 1
                
            except Exception as e:
                error_msg = str(e)
                # Ignore "already exists" errors
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    print(f"  [{i}/{total}] ⊙ {statement_type} (already exists)")
                    success_count += 1
                else:
                    print(f"  [{i}/{total}] ✗ {statement_type}")
                    print(f"      Error: {error_msg}")
                    error_count += 1
        
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"  Total statements: {total}")
        print(f"  Successfully executed: {success_count}")
        print(f"  Errors: {error_count}")
        print("="*60 + "\n")
        
        if error_count == 0:
            print("✅ All migrations applied successfully!\n")
        else:
            print(f"⚠️  {error_count} errors occurred. Please review the output above.\n")
        
        # Verify new tables
        print("Verifying new tables...")
        tables_to_check = [
            'return_requests',
            'inventory_transactions',
            'low_stock_alerts',
            'order_tracking',
            'product_views',
            'sales_analytics',
            'cache_entries'
        ]
        
        for table in tables_to_check:
            try:
                result = db.execute_query(
                    f"SELECT COUNT(*) as count FROM {table}",
                    fetch=True,
                    fetchone=True
                )
                print(f"  ✓ Table '{table}' exists (rows: {result['count']})")
            except Exception as e:
                print(f"  ✗ Table '{table}' not found or error: {e}")
        
        print("\n✅ Migration process completed!\n")
        
        print("="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Restart your Flask application")
        print("2. Test the new features:")
        print("   - Returns/Refunds: /returns/my-returns")
        print("   - Wishlist: /wishlist/")
        print("   - Inventory alerts: Check seller dashboard")
        print("3. Review Redis caching logs in the console")
        print("="*60 + "\n")
        
    except FileNotFoundError:
        print(f"✗ SQL file not found: {sql_file_path}")
        print("  Make sure enhanced_features_schema.sql exists in the database folder.")
        return False
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
