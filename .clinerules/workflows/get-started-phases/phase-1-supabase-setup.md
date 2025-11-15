# Phase 1: Supabase Local Setup [MANDATORY]

**Purpose:** Complete database setup with all entities, security policies, and seed data

**Prerequisites:** 
- Phase 0 completed with requirements documented
- Supabase CLI installed
- Docker Desktop running

**References:**
- `.clinerules/supabase/database/create_migrations.md`
- `.clinerules/supabase/database/create_rls_policies.md`
- `.clinerules/supabase/database/postgres_sql_style_guide.md`

---

## Overview

This phase establishes the complete database foundation:
- Local Supabase instance running via Docker
- All entity tables created with proper migrations
- Row Level Security (RLS) policies on every table
- Seed data for testing and development

**All data models from Phase 0 must be implemented in this phase.**

---

## Step 1: Initialize Supabase

### Install Supabase CLI (if not already installed)

**macOS:**
```bash
brew install supabase/tap/supabase
```

**Other platforms:** See [Supabase CLI Getting Started](https://supabase.com/docs/guides/local-development/cli/getting-started)

### Initialize Supabase Project

```bash
# Create the supabase_ directory first
mkdir supabase_
cd supabase_

# Initialize Supabase in the current directory
supabase init
```

This creates the `supabase_/` directory with:
- `config.toml` - Supabase configuration
- `seed.sql` - Seed data file
- `migrations/` - Database migration files

### Start Local Supabase

```bash
supabase start
```

**Important:** This command will output critical information:

```
API URL: http://127.0.0.1:54321
GraphQL URL: http://127.0.0.1:54321/graphql/v1
DB URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
Studio URL: http://127.0.0.1:54323
Inbucket URL: http://127.0.0.1:54324
JWT secret: super-secret-jwt-token-with-at-least-32-characters-long
anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Save these values!** You'll need the API URL and anon key for Phase 2.

---

## Step 2: Create Profiles Table (Authentication Foundation)

### Create Migration

```bash
supabase migration new create_profiles_table
```

### Write Migration SQL

**File:** `supabase_/migrations/<timestamp>_create_profiles_table.sql`

```sql
-- Create profiles table linked to auth.users
create table profiles (
  id uuid primary key references auth.users on delete cascade,
  full_name text,
  avatar_url text,
  bio text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
comment on table profiles is 'Extended user profile information';

-- Enable Row Level Security
alter table profiles enable row level security;

-- RLS Policies (separate policy for each operation)
create policy "Public profiles are viewable by everyone"
on profiles for select
to authenticated, anon
using (true);

create policy "Users can insert their own profile"
on profiles for insert
to authenticated
with check ((select auth.uid()) = id);

create policy "Users can update their own profile"
on profiles for update
to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

create policy "Users can delete their own profile"
on profiles for delete
to authenticated
using ((select auth.uid()) = id);

-- ⚠️ CRITICAL: Trigger function must use SECURITY DEFINER
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer  -- MUST be SECURITY DEFINER, not SECURITY INVOKER
set search_path = ''
as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (
    new.id,
    new.raw_user_meta_data->>'full_name',
    new.raw_user_meta_data->>'avatar_url'
  );
  return new;
end;
$$;

-- Trigger to create profile on signup
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ⚠️ CRITICAL: Grant permissions for the trigger to work
grant usage on schema public to supabase_auth_admin;
grant insert on public.profiles to supabase_auth_admin;
```

**Why these settings are critical:**
- `SECURITY DEFINER` allows the trigger to bypass RLS policies
- `grant insert` gives auth admin permission to create profiles
- Without these, user signup will fail with "permission denied"

---

## Step 3: Create Application Entity Tables

For **each entity** identified in Phase 0, create a migration and implement the table.

### Migration Naming Convention

Use descriptive names that match your entities:
```bash
supabase migration new create_scenarios_table
supabase migration new create_actors_table
supabase migration new create_timesteps_table
```

### Entity Table Template

**Read:** `.clinerules/supabase/database/create_migrations.md` for complete patterns

**Basic structure for each entity:**

```sql
-- Create [entity] table
create table [entity_name] (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users on delete cascade not null,
  name text not null,
  description text,
  status text default 'active',
  -- Add entity-specific fields here
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
comment on table [entity_name] is 'Description of what this entity represents';

-- Add indexes
create index [entity_name]_user_id_idx on [entity_name](user_id);
create index [entity_name]_status_idx on [entity_name](status);

-- Enable RLS
alter table [entity_name] enable row level security;

-- RLS Policies (one per operation for each role)
create policy "Users can view their own [entity_name]"
on [entity_name] for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can insert their own [entity_name]"
on [entity_name] for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "Users can update their own [entity_name]"
on [entity_name] for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "Users can delete their own [entity_name]"
on [entity_name] for delete
to authenticated
using ((select auth.uid()) = user_id);
```

### Key Requirements for Each Table

**Read:** `.clinerules/supabase/database/postgres_sql_style_guide.md` for style guide

✅ **Must Have:**
- Primary key (usually `id bigint generated always as identity`)
- User relationship (`user_id uuid references auth.users`)
- Timestamps (`created_at`, `updated_at`)
- Appropriate indexes (especially on foreign keys)
- RLS enabled
- Separate RLS policies for each operation (select, insert, update, delete)
- Table and column comments

✅ **Best Practices:**
- Use lowercase snake_case for all names
- Add status/state fields where applicable
- Include soft delete support if needed
- Add constraints for data validation
- Use appropriate data types

### Handling Relationships

**One-to-Many:**
```sql
-- Child table has foreign key to parent
create table child_entity (
  id bigint generated always as identity primary key,
  parent_id bigint references parent_entity on delete cascade not null,
  -- other fields
);
create index child_entity_parent_id_idx on child_entity(parent_id);
```

**Many-to-Many:**
```sql
-- Create junction table
create table entity_a_entity_b (
  entity_a_id bigint references entity_a on delete cascade,
  entity_b_id bigint references entity_b on delete cascade,
  created_at timestamptz default now(),
  primary key (entity_a_id, entity_b_id)
);
create index entity_a_entity_b_a_idx on entity_a_entity_b(entity_a_id);
create index entity_a_entity_b_b_idx on entity_a_entity_b(entity_b_id);
```

---

## Step 4: Apply Migrations

After creating all migration files:

```bash
supabase db reset
```

This command:
1. Drops and recreates the database
2. Applies all migrations in order
3. Runs the seed data

**Verify in terminal:** You should see each migration applied successfully.

---

## Step 5: Create Seed Data

### Edit seed.sql

**File:** `supabase_/seed.sql`

**Read:** `.clinerules/supabase/database/create_migrations.md` for seed data patterns

### Create Test User

```sql
-- Create a test user for development
insert into auth.users (
  id,
  instance_id,
  email,
  encrypted_password,
  email_confirmed_at,
  raw_app_meta_data,
  raw_user_meta_data,
  created_at,
  updated_at,
  role,
  aud
) values (
  '00000000-0000-0000-0000-000000000000',
  '00000000-0000-0000-0000-000000000000',
  'demo@example.com',
  crypt('demo123', gen_salt('bf')),
  now(),
  '{"provider": "email", "providers": ["email"]}'::jsonb,
  '{"full_name": "Demo User"}'::jsonb,
  now(),
  now(),
  'authenticated',
  'authenticated'
);
```

### Seed Entity Data

For **each entity**, add realistic seed data:

```sql
-- Seed [entity_name] data
insert into [entity_name] (user_id, name, description, status) values
  ('00000000-0000-0000-0000-000000000000', 'Example 1', 'Description for example 1', 'active'),
  ('00000000-0000-0000-0000-000000000000', 'Example 2', 'Description for example 2', 'active'),
  ('00000000-0000-0000-0000-000000000000', 'Example 3', 'Description for example 3', 'draft');
```

**Important:** 
- Use the test user's UUID for all user_id fields
- Include variety in the data (different statuses, types, etc.)
- Add enough data to test pagination if needed (10-20 records per entity)
- Make data realistic to the application domain

### Apply Seed Data

```bash
supabase db reset
```

---

## Step 6: Verify Database in Supabase Studio

### Open Supabase Studio

Navigate to: [http://127.0.0.1:54323](http://127.0.0.1:54323)

### Verification Checklist

Navigate through the Studio interface and verify:

**Table Editor:**
- [ ] All tables created (profiles + all entities)
- [ ] Seed data visible in each table
- [ ] Correct number of records
- [ ] Data looks realistic

**Authentication:**
- [ ] Test user exists in Users table
- [ ] Email: demo@example.com
- [ ] Profile created automatically

**Database > Tables:**
- [ ] All tables show correct column types
- [ ] Primary keys configured
- [ ] Foreign keys configured
- [ ] Indexes created

**Database > Policies:**
- [ ] RLS enabled on all tables
- [ ] Policies exist for each operation (select, insert, update, delete)
- [ ] Policies properly scoped to user_id

**SQL Editor:**
Test that RLS works:
```sql
-- This should return all records (you're using service_role in Studio)
select * from scenarios;

-- Test that regular queries work
select 
  s.*,
  p.full_name as user_name
from scenarios s
join profiles p on p.id = s.user_id;
```

---

## Step 7: Document Database Schema

Create a reference document for the database schema.

**File:** `DATABASE_SCHEMA.md` (in project root)

```markdown
# Database Schema

## Tables

### profiles
Extended user information linked to auth.users

**Columns:**
- id (uuid, PK, FK to auth.users)
- full_name (text)
- avatar_url (text)
- bio (text)
- created_at (timestamptz)
- updated_at (timestamptz)

**RLS:** Users can view all, edit own

---

### [entity_name]
[Description of entity]

**Columns:**
- id (bigint, PK)
- user_id (uuid, FK to auth.users)
- name (text, required)
- description (text)
- status (text, default 'active')
- created_at (timestamptz)
- updated_at (timestamptz)

**Relationships:**
- Belongs to: User (profiles)
- Has many: [Related entities]

**RLS:** Users can only access their own records

---

[Repeat for each entity]

## Seed Data

**Test User:**
- Email: demo@example.com
- Password: demo123

**Seed Data Count:**
- [Entity 1]: [count] records
- [Entity 2]: [count] records
- [Entity 3]: [count] records
```

---

## Common Issues and Solutions

### Issue 1: Migration fails with "permission denied"

**Cause:** RLS policies blocking migration operations

**Solution:** 
- Migrations run as `postgres` superuser, should always work
- Check for syntax errors in SQL
- Ensure proper schema qualification (e.g., `auth.users` not just `users`)

### Issue 2: Trigger not creating profiles on signup

**Cause:** Missing `SECURITY DEFINER` or missing grants

**Solution:**
```sql
-- Function must be SECURITY DEFINER
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer  -- Required!
set search_path = ''
as $$
-- function body
$$;

-- Must grant permissions
grant usage on schema public to supabase_auth_admin;
grant insert on public.profiles to supabase_auth_admin;
```

### Issue 3: Seed data not appearing

**Cause:** 
- Wrong user UUID
- RLS blocking inserts
- Migration errors

**Solution:**
- Use exact UUID: `00000000-0000-0000-0000-000000000000`
- Check `supabase db reset` output for errors
- Verify in Supabase Studio Table Editor

### Issue 4: Foreign key constraint violations

**Cause:** Inserting child records before parent records

**Solution:** Order seed data correctly:
1. Auth users
2. Profiles (auto-created via trigger)
3. Parent entities
4. Child entities
5. Junction tables

---

## Step 8: Per-User Seed Data Implementation [RECOMMENDED]

### Why Create Seed Data Per User

Instead of creating a single shared test user, create seed data for each new user automatically:

**Benefits:**
- Users get immediate value - data to explore right after signup
- No shared demo user complications
- Better testing of user isolation/RLS policies
- More realistic onboarding experience
- Each user has their own private data from the start

### Implementation Strategy

1. Create a `seed_user_data()` function that inserts data for a specific user
2. Call it from the `handle_new_user()` trigger after profile creation
3. Ensure proper RLS policies allow users to only see their own data

### Critical Checklist Before Implementation

Before writing the seed data function:

- [ ] Check ALL table schemas for primary key types (bigint vs uuid)
- [ ] Verify profile table column names (don't assume email exists)
- [ ] List all tables that need seed data
- [ ] Plan the order of inserts (handle foreign keys correctly)
- [ ] Identify any junction tables that need seed data

### Complete Implementation Example

Create a new migration: `YYYYMMDDHHMMSS_seed_data_for_new_users.sql`

```sql
-- Migration: YYYYMMDDHHMMSS_seed_data_for_new_users.sql

-- First, create the seed data function
create or replace function public.seed_user_data(p_user_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  -- CRITICAL: Match types to your table schemas!
  -- If your tables use: id bigint generated always as identity
  -- Then declare: bigint NOT uuid
  entity_1_id bigint;
  entity_2_id bigint;
  entity_3_id bigint;
  -- Add more as needed for your entities
begin
  -- Insert seed data for each primary entity
  -- Note: public. prefix required with set search_path = ''
  
  insert into public.entity_1 (user_id, name, description, status)
  values (p_user_id, 'Sample Entity 1', 'First example entity', 'active')
  returning id into entity_1_id;
  
  insert into public.entity_1 (user_id, name, description, status)
  values (p_user_id, 'Sample Entity 2', 'Second example entity', 'active')
  returning id into entity_2_id;
  
  insert into public.entity_2 (user_id, name, type)
  values (p_user_id, 'Sample Entity Type A', 'type_a')
  returning id into entity_3_id;
  
  -- If you have junction tables, insert relationships
  insert into public.entity_1_entity_2 (entity_1_id, entity_2_id)
  values 
    (entity_1_id, entity_3_id),
    (entity_2_id, entity_3_id);
    
exception
  when others then
    -- Log error but don't fail user creation
    raise warning 'Error creating seed data for user %: %', p_user_id, SQLERRM;
end;
$$;

-- Grant necessary permissions to auth admin
grant usage on schema public to supabase_auth_admin;
grant execute on function public.seed_user_data(uuid) to supabase_auth_admin;

-- Update the handle_new_user trigger to call seed function
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  -- Create profile (ONLY include columns that exist in your profiles table)
  insert into public.profiles (id, full_name, avatar_url, updated_at)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'full_name', 'User'),
    coalesce(new.raw_user_meta_data->>'avatar_url', ''),
    now()
  );

  -- Create seed data for this new user
  perform public.seed_user_data(new.id);
  
  return new;
end;
$$;

-- Ensure trigger is properly set up
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Grant insert permissions on all tables that seed_user_data uses
grant insert on public.profiles to supabase_auth_admin;
grant insert on public.entity_1 to supabase_auth_admin;
grant insert on public.entity_2 to supabase_auth_admin;
grant insert on public.entity_1_entity_2 to supabase_auth_admin;
-- Add grants for all other tables used in seed_user_data
```

### Critical Gotchas: Four Common Errors

#### 1. Variable Type Mismatch (MOST COMMON)

**Error:** `invalid input syntax for type uuid: '34'`

**Cause:** Declaring variables as `uuid` when tables use `bigint` for primary keys

**Solution:**
```sql
-- Check your table schema first!
-- If CREATE TABLE shows: id bigint generated always as identity

-- ❌ WRONG
declare
  entity_id uuid;  -- Type mismatch!
begin
  insert into public.entities (...) 
  returning id into entity_id;  -- Returns bigint but expects uuid
end;

-- ✅ CORRECT
declare
  entity_id bigint;  -- Matches table schema
begin
  insert into public.entities (...) 
  returning id into entity_id;  -- bigint to bigint - works!
end;
```

**Quick Check:**
```sql
-- Run in Supabase Studio SQL editor to verify column types:
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'your_table' AND column_name = 'id';
```

#### 2. Missing Schema Qualification

**Error:** `relation "entities" does not exist`

**Cause:** Using `set search_path = ''` for security without qualifying table names

**Solution:**
```sql
-- With set search_path = '', you MUST use public. prefix

-- ❌ WRONG
insert into entities (user_id, name) values (...);

-- ✅ CORRECT
insert into public.entities (user_id, name) values (...);
```

#### 3. Profile Schema Mismatch

**Error:** `column "email" of relation "profiles" does not exist`

**Cause:** Assuming profile table has email column when it doesn't

**Solution:**
```sql
-- Check your profiles table schema! Common columns are:
-- id, full_name, avatar_url, updated_at (NOT email)

-- ❌ WRONG (assuming email exists)
insert into public.profiles (id, email, full_name) values (...);

// ✅ CORRECT (only columns that exist)
insert into public.profiles (id, full_name, avatar_url) values (...);
```

#### 4. Parameter Name Collision

**Error:** Ambiguous column reference or unexpected behavior

**Cause:** Parameter name matches column name (e.g., `user_id`)

**Solution:**
```sql
-- ❌ RISKY - parameter name matches column name
create function seed_user_data(user_id uuid) as $$
begin
  insert into public.entities (user_id) values (user_id);  -- Ambiguous!
end;
$$;

-- ✅ SAFE - prefix parameters to avoid collision
create function seed_user_data(p_user_id uuid) as $$
begin
  insert into public.entities (user_id) values (p_user_id);  -- Clear!
end;
$$;
```

### Verification Steps

After creating your seed data migration:

1. [ ] Run `supabase db reset` to apply all migrations
2. [ ] Check terminal output for any errors
3. [ ] Sign up a new test user through the UI
4. [ ] Verify seed data appears in the dashboard immediately
5. [ ] Check Supabase Studio to confirm data was created
6. [ ] Test that RLS policies allow user to see their data
7. [ ] Verify user can perform CRUD operations on their seed data
8. [ ] Create a second test user and verify users can't see each other's data

---

## Common Database Issues and Solutions

### Issue 1: "Database error saving new user" on signup

**Cause:** Profile trigger doesn't have correct permissions

**Solution:** Ensure migration includes:
```sql
security definer  -- Function must use SECURITY DEFINER
grant usage on schema public to supabase_auth_admin;
grant insert on public.profiles to supabase_auth_admin;
```

### Issue 2: "invalid input syntax for type uuid" errors during user creation

**Cause:** Variable type mismatch in seed_user_data function

**Solution:** 
1. Check table schemas to confirm primary key types
2. If using `bigint` (auto-increment), declare all ID variables as `bigint`, not `uuid`
3. Update function declarations to match table schema

### Issue 3: "relation does not exist" errors in database functions

**Cause:** Functions using `set search_path = ''` for security require schema qualification

**Solution:** Prefix ALL table references with `public.` in functions with empty search path

### Issue 4: "column ambiguity" or parameter naming conflicts

**Cause:** Function parameter name matches a column name

**Solution:** Prefix function parameters with `p_` to avoid conflicts

### Issue 5: Seed data not appearing for new users

**Possible Causes & Solutions:**

1. **Missing grants** - Add grant statements for all tables used in seed_user_data
2. **Function not being called** - Verify trigger is properly attached to auth.users
3. **Silent errors** - Check Supabase logs for warnings from exception handler
4. **RLS blocking** - Verify RLS policies allow insert for authenticated users

---

## Phase 1 Completion Checklist

Before proceeding to Phase 2, verify:

- [ ] Supabase started successfully
- [ ] API URL and anon key saved
- [ ] Profiles table created with trigger
- [ ] All entity tables created (minimum 3)
- [ ] RLS enabled on all tables
- [ ] RLS policies created for all operations
- [ ] Per-user seed data function created
- [ ] Seed data function tested with new user signup
- [ ] All migrations applied successfully
- [ ] Database verified in Supabase Studio
- [ ] Database schema documented
- [ ] User isolation verified (users can't see each other's data)

**Cannot proceed to Phase 2 without complete, working database.**

---

## Next Phase

**Proceed to:** [Phase 2: Next.js Application Setup](./phase-2-nextjs-setup.md)

**With:** 
- Supabase running locally
- API URL and anon key saved
- Complete database with all entities
- Per-user seed data automatically created on signup
- RLS policies ensuring data isolation
