import os
import re

models_dir = r"c:\Users\JM\Downloads\pawfect-finds\app\models"

print("=" * 80)
print("SCANNING ALL MODELS FOR MySQL execute_query USAGE")
print("=" * 80)

models_status = []

for filename in os.listdir(models_dir):
    if filename.endswith('.py') and not filename.startswith('__'):
        filepath = os.path.join(models_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count execute_query occurrences
        execute_query_count = len(re.findall(r'\.execute_query\(', content))
        
        # Check if it uses Supabase methods
        uses_supabase = bool(re.search(r'db\.select\(|db\.insert\(|db\.update\(|db\.delete\(|db\.client\.table\(', content))
        
        status = "✅ CONVERTED" if execute_query_count == 0 else f"❌ NEEDS FIX ({execute_query_count} calls)"
        
        models_status.append({
            'file': filename,
            'status': status,
            'count': execute_query_count,
            'uses_supabase': uses_supabase
        })

# Sort by count (highest first)
models_status.sort(key=lambda x: x['count'], reverse=True)

print(f"\n{'FILE':<30} {'STATUS':<25} {'SUPABASE':<10}")
print("-" * 80)

for model in models_status:
    supabase_status = "Yes" if model['uses_supabase'] else "No"
    print(f"{model['file']:<30} {model['status']:<25} {supabase_status:<10}")

total_files = len(models_status)
converted = sum(1 for m in models_status if m['count'] == 0)
needs_fix = total_files - converted
total_calls = sum(m['count'] for m in models_status)

print("\n" + "=" * 80)
print(f"SUMMARY:")
print(f"  Total model files: {total_files}")
print(f"  ✅ Converted to Supabase: {converted}")
print(f"  ❌ Still using MySQL: {needs_fix}")
print(f"  Total execute_query calls remaining: {total_calls}")
print("=" * 80)

if needs_fix > 0:
    print(f"\n⚠️  {needs_fix} model files still need conversion!")
    print("\nPriority files to fix (most calls first):")
    for model in models_status[:5]:
        if model['count'] > 0:
            print(f"  - {model['file']}: {model['count']} calls")
