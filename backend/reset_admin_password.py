"""
Quick script to reset admin password
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database_service import supabase
import bcrypt

print("="*60)
print("RESET ADMIN PASSWORD")
print("="*60)

# Generate new password hash
password = "Admin@123456"
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

print("\n1. Updating admin password...")
try:
    # Update the admin password
    result = supabase.table("admins").update({
        "password_hash": password_hash.decode('utf-8')
    }).eq("email", "admin@example.com").execute()
    
    if result.data and len(result.data) > 0:
        print("   ✅ Password updated successfully!")
        print("\n" + "="*60)
        print("NEW LOGIN CREDENTIALS")
        print("="*60)
        print("Email:    admin@example.com")
        print("Password: Admin@123456")
        print("\nYou can now login at: http://localhost:3000/admin/login")
    else:
        print("   ⚠️  No admin found to update")
        print("   Run: python create_admin.py")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
