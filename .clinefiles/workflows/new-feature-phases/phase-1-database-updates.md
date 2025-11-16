# Phase 1: Database Schema Updates [IF NEEDED]

**Purpose:** Implement database changes for the new feature

**Prerequisites:**
- Phase 0 complete with approved FEATURE_PLAN.md
- Database changes designed and documented
- SYSTEM_REFERENCE.md reviewed for existing schema
- Supabase running locally

**Execute this phase if:** Feature requires new tables, columns, relationships, or RLS policy updates

**Skip this phase if:** Feature uses only existing database structures without modifications

**References:**
- `.clinefiles/supabase/database/create_migrations.md`
- `.clinefiles/supabase/database/create_rls_policies.md`
- `.clinefiles/supabase/database/postgres_sql_style_guide.md`
- `.clinefiles/supabase/database/declarative_schema.md`

---

## Overview

Phase 1 implements the database changes planned in Phase 0. This phase ensures:

1. **Migration Created** - Following naming conventions
2. **Tables/Columns Added** - With proper types and constraints
3. **RLS Policies Applied** - Security on all new/modified tables
4. **Relationships Established** - Foreign keys and indexes
5. **User Isolation Tested** - Verify RLS works correctly
6. **Documentation Updated** - DATABASE_SCHEMA.md reflects changes

**All database changes must maintain data security and user isolation.**

---

## Step 1: Review Feature Plan Database Design

### Re-read FEATURE_PLAN.md Section 3

**Extract from FEATURE_PLAN.md:**
- New tables to create
- Columns to add to existing tables
- Relationships to establish
- RLS policies needed
- Migration strategy

### Cross-Reference Existing Schema

**Open SYSTEM_REFERENCE.md and review:**
- Current database schema
- Naming conventions used
- Existing relationships
- Pattern for RLS policies

**Ensure consistency:**
- Table names follow project convention (lowercase_snake_case)
- Column names match existing patterns
- Foreign key naming consistent
- RLS policy patterns match existing

---

## Step 2: Create Migration File

### Generate Migration

```bash
supabase migration new feature_name_description
```

**Naming convention:**
- Use descriptive name that indicates what changes
- Format: `feature_name_table_action`
- Examples:
  - `notification_preferences_table`
  - `add_status_to_tasks`
  - `user_settings_and_preferences`

**Migration file location:**
```
supabase/migrations/YYYYMMDDHHmmss_feature_name_description.sql
```

### Migration File Structure

**Template:**

```sql
-- Migration: [Feature Name] - [Description]
-- Created: [Date]
-- Purpose: [What this migration accomplishes]

-- ============================================================================
-- SECTION 1: Create New Tables (if applicable)
-- ============================================================================

[Table creation SQL]

-- ============================================================================
-- SECTION 2: Modify Existing Tables (if applicable)
-- ============================================================================

[ALTER TABLE statements]

-- ============================================================================
-- SECTION 3: Create Relationships (if applicable)
-- ============================================================================

[Foreign key constraints, indexes]

-- ============================================================================
-- SECTION 4: Enable RLS and Create Policies
-- ============================================================================

[RLS policies for all affected tables]

-- ============================================================================
-- SECTION 5: Functions and Triggers (if applicable)
-- ============================================================================

[Any custom functions or triggers]

-- ============================================================================
-- SECTION 6: Grants and Permissions (if applicable)
-- ============================================================================

[Permission grants for functions/tables]
```

---

## Step 3: Implement New Tables

### For Each New Table

**From FEATURE_PLAN.md, implement table design:**

```sql
-- Create [table_name] table
create table [table_name] (
  -- Primary key
  id bigint generated always as identity primary key,
  
  -- User reference (for user-scoped data)
  user_id uuid references auth.users on delete cascade not null,
  
  -- Feature-specific fields
  [field_name] [data_type] [constraints],
  
  -- Timestamps (always include)
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Add table comment (REQUIRED - documents purpose)
comment on table [table_name] is '[Description of what this table stores]';

-- Add column comments for complex fields
comment on column [table_name].[field_name] is '[Description of field purpose]';
```

### Standard Patterns to Follow

**Primary Keys:**
```sql
-- Auto-incrementing integer (most common)
id bigint generated always as identity primary key

-- UUID (when needed for distributed systems or external references)
id uuid default gen_random_uuid() primary key
```

**User Relationships:**
```sql
-- User-scoped data (most common)
user_id uuid references auth.users on delete cascade not null

-- Optional user relationship
user_id uuid references auth.users on delete cascade

-- System data (not user-specific)
-- Omit user_id column
```

**Timestamps:**
```sql
-- Always include both (convention)
created_at timestamptz default now(),
updated_at timestamptz default now()
```

**Status/State Fields:**
```sql
-- Use CHECK constraints for valid values
status text not null default 'active' check (status in ('active', 'inactive', 'archived')),

-- Or use ENUM types (if many states)
CREATE TYPE [type_name] AS ENUM ('value1', 'value2', 'value3');
state [type_name] not null default 'value1'
```

### Add Indexes

**Index foreign keys:**
```sql
create index [table_name]_user_id_idx on [table_name](user_id);
create index [table_name]_parent_id_idx on [table_name](parent_id);
```

**Index frequently queried columns:**
```sql
-- Status fields used in WHERE clauses
create index [table_name]_status_idx on [table_name](status);

-- Date fields used for sorting/filtering
create index [table_name]_created_at_idx on [table_name](created_at desc);
```

**Composite indexes for common queries:**
```sql
-- User + status queries
create index [table_name]_user_status_idx on [table_name](user_id, status);
```

---

## Step 4: Modify Existing Tables

### Add Columns to Existing Tables

**Pattern:**

```sql
-- Add new column to existing table
alter table [existing_table] 
  add column [new_column] [data_type] [constraints];

-- Add comment
comment on column [existing_table].[new_column] is '[Description]';

-- Add index if needed
create index [existing_table]_[new_column]_idx on [existing_table]([new_column]);
```

**Examples:**

```sql
-- Add nullable column (safe - no backfill needed)
alter table scenarios 
  add column visibility text default 'private' check (visibility in ('private', 'team', 'public'));

-- Add column with default (safe - auto-populates)
alter table profiles
  add column notification_email text default null;

-- Add NOT NULL column (requires strategy)
-- Option 1: Add with default first, then make NOT NULL
alter table tasks add column priority text default 'medium';
alter table tasks alter column priority set not null;

-- Option 2: Add nullable, backfill, then make NOT NULL
alter table tasks add column assigned_to uuid references auth.users;
-- Manually update existing rows
update tasks set assigned_to = user_id where assigned_to is null;
alter table tasks alter column assigned_to set not null;
```

### Handle Existing Data

**If modifying columns with existing data:**

**Safe changes:**
- Adding nullable columns
- Adding columns with defaults
- Increasing varchar limits
- Making columns nullable

**Risky changes requiring migration strategy:**
- Adding NOT NULL columns (need default or backfill)
- Changing column types (may require casting)
- Removing columns (ensure not in use)
- Changing constraints (validate data first)

**Migration strategy pattern:**

```sql
-- 1. Add new column
alter table [table] add column [new_column] [type];

-- 2. Backfill data from old column
update [table] set [new_column] = [old_column];

-- 3. Make NOT NULL if needed
alter table [table] alter column [new_column] set not null;

-- 4. Drop old column (optional, or rename for rollback safety)
-- alter table [table] drop column [old_column];
alter table [table] rename column [old_column] to [old_column]_deprecated;
```

---

## Step 5: Establish Relationships

### Foreign Key Constraints

**One-to-Many Relationships:**

```sql
-- Child table references parent
alter table [child_table]
  add constraint [child_table]_[parent_table]_fkey
  foreign key ([parent_id]) 
  references [parent_table](id) 
  on delete cascade;

-- Add index on foreign key
create index [child_table]_[parent_id]_idx on [child_table]([parent_id]);
```

**On Delete Behaviors:**

```sql
-- CASCADE - delete children when parent deleted (most common)
on delete cascade

-- RESTRICT - prevent parent deletion if children exist
on delete restrict

-- SET NULL - set foreign key to null when parent deleted
on delete set null

-- SET DEFAULT - set foreign key to default when parent deleted
on delete set default
```

**Example:**

```sql
-- Task belongs to Scenario
-- When scenario deleted, delete all tasks
alter table tasks
  add constraint tasks_scenario_fkey
  foreign key (scenario_id)
  references scenarios(id)
  on delete cascade;

create index tasks_scenario_id_idx on tasks(scenario_id);
```

### Many-to-Many Relationships

**Create junction table:**

```sql
-- Create junction table for many-to-many
create table [entity_a]_[entity_b] (
  [entity_a]_id bigint references [entity_a](id) on delete cascade not null,
  [entity_b]_id bigint references [entity_b](id) on delete cascade not null,
  
  -- Optional: additional fields
  role text,
  created_at timestamptz default now(),
  
  -- Composite primary key
  primary key ([entity_a]_id, [entity_b]_id)
);

comment on table [entity_a]_[entity_b] is 'Junction table linking [entity_a] and [entity_b]';

-- Indexes for both directions
create index [entity_a]_[entity_b]_a_idx on [entity_a]_[entity_b]([entity_a]_id);
create index [entity_a]_[entity_b]_b_idx on [entity_a]_[entity_b]([entity_b]_id);
```

**Example:**

```sql
-- Users can be members of multiple teams
-- Teams can have multiple users
create table team_members (
  team_id bigint references teams(id) on delete cascade not null,
  user_id uuid references auth.users(id) on delete cascade not null,
  role text not null default 'member' check (role in ('owner', 'admin', 'member')),
  joined_at timestamptz default now(),
  primary key (team_id, user_id)
);

create index team_members_team_idx on team_members(team_id);
create index team_members_user_idx on team_members(user_id);
```

---

## Step 6: Implement RLS Policies

### Enable RLS on All New Tables

**CRITICAL:** Every table with user data must have RLS enabled.

```sql
-- Enable RLS (REQUIRED)
alter table [table_name] enable row level security;
```

### Create Policies for Each Operation

**Read `.clinefiles/supabase/database/create_rls_policies.md` for comprehensive patterns.**

**Standard pattern - separate policy per operation:**

```sql
-- SELECT policy
create policy "[Table] - users can view own records"
on [table_name] for select
to authenticated
using ((select auth.uid()) = user_id);

-- INSERT policy
create policy "[Table] - users can insert own records"
on [table_name] for insert
to authenticated
with check ((select auth.uid()) = user_id);

-- UPDATE policy
create policy "[Table] - users can update own records"
on [table_name] for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

-- DELETE policy
create policy "[Table] - users can delete own records"
on [table_name] for delete
to authenticated
using ((select auth.uid()) = user_id);
```

### Junction Table RLS

**For many-to-many junction tables:**

```sql
-- Users can view relationships they're part of
create policy "[Junction] - users can view own relationships"
on [entity_a]_[entity_b] for select
to authenticated
using (
  user_id = (select auth.uid())
  or 
  exists (
    select 1 from [entity_a]
    where id = [entity_a]_id and user_id = (select auth.uid())
  )
);

-- Similar patterns for INSERT/UPDATE/DELETE
-- Ensure user owns at least one side of the relationship
```

### Update Existing Table RLS (If Needed)

**If feature adds columns requiring policy changes:**

```sql
-- Drop old policy
drop policy if exists "[old_policy_name]" on [table_name];

-- Create updated policy
create policy "[updated_policy_name]"
on [table_name] for [operation]
to authenticated
[updated using/with check clause];
```

---

## Step 7: Test Migration

### Apply Migration

```bash
# Reset database to apply all migrations
supabase db reset
```

**Verify in terminal output:**
- [ ] All migrations applied successfully
- [ ] No errors or warnings
- [ ] Seed data applied (if you have seed.sql)

### Verify in Supabase Studio

**Navigate to:** http://localhost:54323

**Check Tables:**
- [ ] New tables exist
- [ ] Columns match specification
- [ ] Data types correct
- [ ] Defaults applied
- [ ] Constraints active

**Check Relationships:**
- [ ] Foreign keys established
- [ ] On delete behavior correct
- [ ] Indexes created

**Check RLS:**
- [ ] RLS enabled on all tables
- [ ] Policies exist for each operation
- [ ] Policy definitions correct

---

## Step 8: Test RLS Policies

### Create Test Users

**In Supabase Studio SQL Editor:**

```sql
-- Create test user 1
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
  '11111111-1111-1111-1111-111111111111',
  '00000000-0000-0000-0000-000000000000',
  'test1@example.com',
  crypt('test123', gen_salt('bf')),
  now(),
  '{"provider": "email", "providers": ["email"]}'::jsonb,
  '{"full_name": "Test User 1"}'::jsonb,
  now(),
  now(),
  'authenticated',
  'authenticated'
);

-- Create test user 2
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
  '22222222-2222-2222-2222-222222222222',
  '00000000-0000-0000-0000-000000000000',
  'test2@example.com',
  crypt('test123', gen_salt('bf')),
  now(),
  '{"provider": "email", "providers": ["email"]}'::jsonb,
  '{"full_name": "Test User 2"}'::jsonb,
  now(),
  now(),
  'authenticated',
  'authenticated'
);
```

### Insert Test Data

```sql
-- Insert data for user 1
insert into [table_name] (user_id, [fields])
values ('11111111-1111-1111-1111-111111111111', [values]);

-- Insert data for user 2
insert into [table_name] (user_id, [fields])
values ('22222222-2222-2222-2222-222222222222', [values]);
```

### Test User Isolation

**Create SQL queries that simulate authenticated users:**

```sql
-- Test as User 1
set local role authenticated;
set local request.jwt.claims.sub to '11111111-1111-1111-1111-111111111111';

-- User 1 should see only their data
select * from [table_name];

-- Reset
reset role;

-- Test as User 2
set local role authenticated;
set local request.jwt.claims.sub to '22222222-2222-2222-2222-222222222222';

-- User 2 should see only their data (different from User 1)
select * from [table_name];

-- Reset
reset role;
```

**Verify:**
- [ ] User 1 sees only their records
- [ ] User 2 sees only their records
- [ ] No cross-user data leakage
- [ ] Counts match expected (e.g., User 1 has 3 records, User 2 has 2 records)

### Test CRUD Operations

**For each user, test:**

```sql
-- Set to test user
set local role authenticated;
set local request.jwt.claims.sub to '11111111-1111-1111-1111-111111111111';

-- Test INSERT
insert into [table_name] (user_id, [fields])
values ('11111111-1111-1111-1111-111111111111', [values]);
-- Should succeed

-- Test UPDATE own record
update [table_name] 
set [field] = [new_value]
where id = [their_record_id];
-- Should succeed

-- Test UPDATE other user's record
update [table_name]
set [field] = [new_value]
where id = [other_user_record_id];
-- Should fail silently (0 rows affected)

-- Test DELETE own record
delete from [table_name] where id = [their_record_id];
-- Should succeed

-- Test DELETE other user's record
delete from [table_name] where id = [other_user_record_id];
-- Should fail silently (0 rows affected)

reset role;
```

---

## Step 9: Update Seed Data (Optional)

### Add Feature-Specific Seed Data

**If feature should have seed data for new users:**

**Edit:** `supabase/seed.sql` or per-user seed function

```sql
-- Add to existing seed data
insert into [new_table] (user_id, [fields]) values
  ('00000000-0000-0000-0000-000000000000', [values]),
  ('00000000-0000-0000-0000-000000000000', [values]);
```

**Or update per-user seed function:**

```sql
-- If you have a seed_user_data() function
create or replace function public.seed_user_data(p_user_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  -- Existing seed data...
  
  -- Add new feature seed data
  insert into public.[new_table] (user_id, [fields])
  values (p_user_id, [values]);
  
exception
  when others then
    raise warning 'Error in seed_user_data: %', SQLERRM;
end;
$$;
```

---

## Step 10: Update Documentation

### Update DATABASE_SCHEMA.md

**Add new table documentation:**

```markdown
### [table_name]
[Description of what this table stores]

**Columns:**
- id (bigint, PK, auto-increment)
- user_id (uuid, FK to auth.users)
- [field_name] ([type], [constraints])
- created_at (timestamptz)
- updated_at (timestamptz)

**Relationships:**
- Belongs to: User (profiles via user_id)
- Has many: [Related entities]
- Related to: [Junction table relationships]

**RLS:** Users can only access their own records

**Indexes:**
- user_id (for user lookups)
- [other_indexed_fields]
```

### Update SYSTEM_REFERENCE.md Database Section

**Add to database schema section:**

```markdown
#### [table_name]
- Purpose: [Description]
- User-scoped: Yes/No
- Relationships: [List key relationships]
```

---

## Common Issues and Solutions

### Issue 1: "permission denied" during migration

**Cause:** Trying to reference objects outside public schema without proper qualification

**Solution:**
```sql
-- ❌ WRONG
references users(id)

-- ✅ CORRECT
references auth.users(id)
```

### Issue 2: RLS policy prevents valid operations

**Symptom:** User can't perform operations they should be able to

**Solution:**
- Check policy USING and WITH CHECK clauses
- Test with actual auth context: `set local request.jwt.claims.sub`
- Ensure `auth.uid()` wrapped in SELECT: `(select auth.uid())`

### Issue 3: Foreign key constraint violation

**Symptom:** "violates foreign key constraint"

**Solution:**
- Check parent record exists before inserting child
- Verify foreign key column references correct parent table/column
- Ensure on delete behavior matches expectations

### Issue 4: "relation already exists"

**Symptom:** Migration fails because table/index exists

**Solution:**
```sql
-- Use IF NOT EXISTS
create table if not exists [table_name] (...);
create index if not exists [index_name] on [table_name]([column]);
```

### Issue 5: Type mismatch in seed data

**Symptom:** "column is of type X but expression is of type Y"

**Solution:**
```sql
-- Cast to correct type
insert into [table] ([column]) values ([value]::[type]);

-- Or use proper literal syntax
-- For UUID:
'00000000-0000-0000-0000-000000000000'::uuid

// For JSONB:
'{"key": "value"}'::jsonb
```

---

## Phase 1 Completion Checklist

Before proceeding to Phase 2:

### Migration
- [ ] Migration file created with descriptive name
- [ ] Migration SQL follows project conventions
- [ ] All SQL formatted according to style guide
- [ ] Comments added for complex logic

### Tables
- [ ] All new tables created
- [ ] All columns match FEATURE_PLAN.md spec
- [ ] Proper data types and constraints
- [ ] Timestamps on all tables
- [ ] Table comments added

### Relationships
- [ ] Foreign keys established
- [ ] On delete behavior correct
- [ ] Indexes on all foreign keys
- [ ] Junction tables for many-to-many

### RLS
- [ ] RLS enabled on all user-scoped tables
- [ ] Separate policy for each operation (SELECT, INSERT, UPDATE, DELETE)
- [ ] Policies tested with simulated users
- [ ] User isolation verified (no data leakage)

### Testing
- [ ] Migration applied successfully
- [ ] Verified in Supabase Studio
- [ ] Two test users created
- [ ] RLS isolation tested
- [ ] CRUD operations tested per user
- [ ] No permission errors for valid operations

### Documentation
- [ ] DATABASE_SCHEMA.md updated
- [ ] SYSTEM_REFERENCE.md updated
- [ ] Comments added to complex SQL

**Cannot proceed until user isolation is verified and all RLS policies tested.**

---

## Next Phase

**Proceed to:** [Phase 2: Frontend Implementation](./phase-2-frontend-implementation.md)

**With:**
- Database changes implemented and tested
- RLS policies verified
- User isolation confirmed
- Documentation updated
- Ready to build UI on top of new schema
