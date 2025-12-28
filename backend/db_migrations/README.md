# Database Migration Scripts

This directory contains SQL migration scripts for setting up the AI Interviewer database in Supabase.

## Migration Order

Run these scripts in order in your Supabase SQL Editor:

### 1. `001_create_tables.sql`
Creates all database tables:
- `candidates` - Stores candidate information
- `interviews` - Tracks interview sessions
- `questions` - Stores generated questions
- `answers` - Stores answers with evaluations
- `admins` - Admin user accounts

Also creates:
- Indexes for query optimization
- Foreign key constraints
- Row Level Security (RLS) policies (enabled by default)
- Triggers for timestamp management

### 2. `002_seed_admin.sql`
Creates a default admin user for initial access.

**Default Credentials:**
- Email: `admin@example.com`
- Password: `Admin@123456`

⚠️ **IMPORTANT**: Change these credentials immediately after first login!

### 3. `003_disable_rls.sql` (Required for Development)
Disables Row Level Security on all tables.

**Why is this needed?**
- By default, Supabase uses the `anon` key which has RLS restrictions
- The backend needs write access to all tables
- For development, it's easier to disable RLS
- For production, use the `service_role` key instead

**Run this script to fix the error:**
```
APIError: 'new row violates row-level security policy for table "candidates"'
```

## How to Run

1. Open your Supabase project
2. Go to SQL Editor
3. Copy and paste the content of `001_create_tables.sql`
4. Click "Run"
5. Repeat for `002_seed_admin.sql`
6. **Repeat for `003_disable_rls.sql`** (IMPORTANT!)

## Verify Installation

After running the migrations, verify in Supabase:

1. Check Table Editor - you should see 5 new tables
2. Check Database → Tables → candidates → Indexes
3. Check Database → Tables → interviews → Foreign Keys
4. Query admins table to verify default user exists:
   ```sql
   SELECT email, created_at FROM admins;
   ```

## RLS Configuration (Optional)

### For Development (Recommended)
Run `003_disable_rls.sql` - This allows the backend to write to tables using the anon key.

### For Production (More Secure)
Instead of disabling RLS, use the service_role key:

1. Get service_role key from Supabase → Settings → API
2. Update `backend/.env`:
   ```env
   SUPABASE_KEY=your-service-role-key-here  # Not the anon key!
   ```
3. DO NOT run `003_disable_rls.sql`

## Rollback

If you need to start fresh:

```sql
-- WARNING: This will delete all data!
DROP TABLE IF EXISTS answers CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS interviews CASCADE;
DROP TABLE IF EXISTS candidates CASCADE;
DROP TABLE IF EXISTS admins CASCADE;
```

Then re-run the migration scripts.
