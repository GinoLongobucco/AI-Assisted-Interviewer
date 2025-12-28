"""
Quick diagnostic script to test Supabase connection
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("="*60)
print("SUPABASE CONNECTION TEST")
print("="*60)

# Check environment variables
print("\n1. Checking environment variables...")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    print("   ❌ SUPABASE_URL not found in .env")
    print("   Please add it to your .env file")
    sys.exit(1)
else:
    # Show partial URL for security
    print(f"   ✓ SUPABASE_URL found: {SUPABASE_URL[:30]}...")

if not SUPABASE_KEY:
    print("   ❌ SUPABASE_KEY not found in .env")
    print("   Please add it to your .env file")
    sys.exit(1)
else:
    print(f"   ✓ SUPABASE_KEY found: {SUPABASE_KEY[:20]}...")

# Test connection
print("\n2. Testing Supabase connection...")
try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✓ Supabase client created successfully")
except Exception as e:
    print(f"   ❌ Failed to create Supabase client: {e}")
    sys.exit(1)

# Test database tables
print("\n3. Checking database tables...")
tables_to_check = ["candidates", "interviews", "questions", "answers", "admins"]

for table in tables_to_check:
    try:
        result = supabase.table(table).select("*").limit(1).execute()
        print(f"   ✓ Table '{table}' exists and is accessible")
    except Exception as e:
        print(f"   ❌ Table '{table}' error: {e}")
        print(f"      Have you run the migration scripts in Supabase?")
        print(f"      See: backend/db_migrations/001_create_tables.sql")

# Test creating a candidate
print("\n4. Testing database write operation...")
try:
    test_email = "diagnostic_test@example.com"
    
    # Check if test candidate exists
    existing = supabase.table("candidates").select("*").eq("email", test_email).execute()
    
    if existing.data and len(existing.data) > 0:
        print(f"   ✓ Test candidate already exists: {test_email}")
    else:
        # Create test candidate
        result = supabase.table("candidates").insert({
            "email": test_email,
            "first_name": "Test",
            "last_name": "User"
        }).execute()
        print(f"   ✓ Successfully created test candidate: {test_email}")
except Exception as e:
    print(f"   ❌ Failed to write to database: {e}")
    print(f"      Check your Supabase permissions and RLS policies")

# Check admin exists
print("\n5. Checking admin user...")
try:
    admin = supabase.table("admins").select("email").eq("email", "admin@example.com").execute()
    if admin.data and len(admin.data) > 0:
        print(f"   ✓ Default admin exists: admin@example.com")
    else:
        print(f"   ⚠ Default admin NOT found")
        print(f"      Run migration: backend/db_migrations/002_seed_admin.sql")
except Exception as e:
    print(f"   ❌ Error checking admin: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print("\nIf all checks passed, your database is ready!")
print("If you see errors, follow the instructions above to fix them.")
print("\nNext steps:")
print("1. Make sure SUPABASE_URL and SUPABASE_KEY are in backend/.env")
print("2. Run migration scripts in Supabase SQL Editor:")
print("   - backend/db_migrations/001_create_tables.sql")
print("   - backend/db_migrations/002_seed_admin.sql")
print("3. Restart the backend server")
