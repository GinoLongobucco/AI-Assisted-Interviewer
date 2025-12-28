"""
Script to create admin user directly from Python
This is a backup method if the SQL script doesn't work
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database_service import create_admin, get_admin_by_email, supabase

print("="*60)
print("ADMIN USER SETUP")
print("="*60)

# Check if admin exists
print("\n1. Checking if admin user exists...")
existing_admin = get_admin_by_email("admin@example.com")

if existing_admin:
    print(f"   ✓ Admin user already exists: {existing_admin['email']}")
    print(f"   Created at: {existing_admin.get('created_at', 'Unknown')}")
    print("\n   You should be able to login with:")
    print("   Email: admin@example.com")
    print("   Password: Admin@123456")
else:
    print("   ⚠ No admin user found in database")
    
    # Create admin user
    print("\n2. Creating admin user...")
    try:
        admin = create_admin("admin@example.com", "Admin@123456")
        print(f"   ✅ Admin user created successfully!")
        print(f"   Email: {admin['email']}")
        print(f"   ID: {admin['id']}")
        
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS")
        print("="*60)
        print("Email:    admin@example.com")
        print("Password: Admin@123456")
        print("\n⚠️  Change this password after first login!")
        
    except Exception as e:
        print(f"   ❌ Failed to create admin: {e}")
        print("\n   Try running this SQL in Supabase SQL Editor:")
        print("   See: backend/db_migrations/002_seed_admin.sql")

print("\n" + "="*60)
print("DONE")
print("="*60)
