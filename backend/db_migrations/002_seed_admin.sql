-- ============================================================================
-- Seed Default Admin User
-- ============================================================================
-- This script creates a default admin user for initial access
-- 
-- Default Credentials:
-- Email: admin@example.com
-- Password: Admin@123456
-- 
-- IMPORTANT: Change these credentials immediately after first login!
-- 
-- The password is hashed using bcrypt with salt rounds = 12

-- Insert default admin user
-- Password hash for "Admin@123456"
INSERT INTO admins (email, password_hash)
VALUES (
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiXMz0pXO'
)
ON CONFLICT (email) DO NOTHING;

-- Success message
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM admins WHERE email = 'admin@example.com') THEN
        RAISE NOTICE 'Default admin user created successfully!';
        RAISE NOTICE 'Email: admin@example.com';
        RAISE NOTICE 'Password: Admin@123456';
        RAISE NOTICE '';
        RAISE NOTICE '⚠️  IMPORTANT: Change this password immediately after first login!';
    ELSE
        RAISE NOTICE 'Admin user already exists, skipping...';
    END IF;
END $$;
