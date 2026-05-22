"""Apply the fixed migration"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database import Database

def apply_fix():
    db = Database()
    
    print("Applying database fixes...")
    
    # Read the SQL file
    sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                           'migrations', 'fix_missing_tables.sql')
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in content.split(';') if s.strip()]
    
    for idx, stmt in enumerate(statements, 1):
        if stmt.upper().startswith('USE') or not stmt or stmt.startswith('--'):
            continue
        
        try:
            print(f"\n[{idx}] Executing: {stmt[:60]}...")
            db.execute_query(stmt)
            print("✓ Success")
        except Exception as e:
            error_msg = str(e).lower()
            # Ignore "already exists" type errors
            if any(x in error_msg for x in ['duplicate', 'exists', 'already']):
                print(f"⚠ Skipped (already exists)")
            else:
                print(f"✗ Error: {e}")
    
    print("\n✅ Migration fixes applied!")

if __name__ == '__main__':
    apply_fix()
