-- ============================================================================
-- DISABLE ROW LEVEL SECURITY (For Development/Testing)
-- ============================================================================
-- This script disables RLS policies to allow the backend to write to tables
-- Run this in Supabase SQL Editor AFTER running 001_create_tables.sql

-- Disable RLS on all tables
ALTER TABLE candidates DISABLE ROW LEVEL SECURITY;
ALTER TABLE interviews DISABLE ROW LEVEL SECURITY;
ALTER TABLE questions DISABLE ROW LEVEL SECURITY;
ALTER TABLE answers DISABLE ROW LEVEL SECURITY;
ALTER TABLE admins DISABLE ROW LEVEL SECURITY;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Row Level Security DISABLED on all tables';
    RAISE NOTICE '';
    RAISE NOTICE 'Your backend can now write to the database!';
    RAISE NOTICE 'This is fine for development/testing.';
    RAISE NOTICE '';
    RAISE NOTICE 'For production, consider using SERVICE_ROLE key instead.';
    RAISE NOTICE 'See: backend/db_migrations/README.md';
END $$;
