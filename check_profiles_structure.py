from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
service_key = os.getenv('SUPABASE_SERVICE_KEY')

client = create_client(url, service_key)

# Get one profile to see structure
response = client.table('profiles').select('*').limit(1).execute()

if response.data:
    print("Profiles table columns:")
    for key in response.data[0].keys():
        print(f"  - {key}")
    print("\nSample profile:")
    print(response.data[0])
