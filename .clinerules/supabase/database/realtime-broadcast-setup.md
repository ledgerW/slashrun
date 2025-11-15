# Realtime Broadcast Setup (Database Side)

**Server-side configuration for Supabase Realtime broadcast triggers**

---

## When to Use Broadcast

Use `broadcast` instead of `postgres_changes` when:
- **Production environment** with many concurrent users
- **Low-latency requirements** (sub-100ms updates)
- **Custom message formats** beyond raw table changes
- **Scalability** is a concern (postgres_changes is single-threaded)

For local development or simple use cases, `postgres_changes` is simpler and works well.

---

## Setup Steps

### 1. Enable Realtime for Table

```sql
-- Enable realtime publication for your table
ALTER PUBLICATION supabase_realtime ADD TABLE your_table;
```

### 2. Create Broadcast Trigger Function

```sql
CREATE OR REPLACE FUNCTION your_table_broadcast_trigger()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
  -- Broadcast to topic-specific channel
  PERFORM realtime.broadcast_changes(
    'topic:' || COALESCE(NEW.id, OLD.id)::text,  -- Channel topic
    TG_OP,                                          -- Event name (INSERT/UPDATE/DELETE)
    TG_OP,                                          -- Operation type
    TG_TABLE_NAME,                                  -- Table name
    TG_TABLE_SCHEMA,                                -- Schema name
    NEW,                                            -- New record
    OLD                                             -- Old record
  );
  RETURN COALESCE(NEW, OLD);
END;
$$;
```

### 3. Create Trigger

```sql
DROP TRIGGER IF EXISTS your_table_broadcast ON your_table;
CREATE TRIGGER your_table_broadcast
  AFTER INSERT OR UPDATE OR DELETE ON your_table
  FOR EACH ROW EXECUTE FUNCTION your_table_broadcast_trigger();
```

### 4. Set Up RLS Policies (Required)

Broadcast uses **private channels** which require RLS policies on `realtime.messages`:

```sql
-- Allow authenticated users to receive broadcasts
CREATE POLICY "users_can_receive_broadcasts" ON realtime.messages
FOR SELECT TO authenticated
USING (
  topic LIKE 'topic:%' AND
  EXISTS (
    SELECT 1 FROM your_table
    WHERE id = SPLIT_PART(topic, ':', 2)::bigint
    AND user_id = auth.uid()
  )
);

-- Allow authenticated users to send broadcasts (if needed)
CREATE POLICY "users_can_send_broadcasts" ON realtime.messages
FOR INSERT TO authenticated
WITH CHECK (
  topic LIKE 'topic:%' AND
  EXISTS (
    SELECT 1 FROM your_table
    WHERE id = SPLIT_PART(topic, ':', 2)::bigint
    AND user_id = auth.uid()
  )
);
```

### 5. Create Performance Index

```sql
-- Index for RLS policy performance
CREATE INDEX IF NOT EXISTS idx_your_table_user_id 
ON your_table(user_id, id);
```

---

## Topic Naming Patterns

### Pattern 1: Entity-Based Topics

```sql
-- One topic per entity
'entity:' || NEW.id::text

-- Examples:
-- 'room:123'
-- 'document:456'
-- 'game:789'
```

### Pattern 2: Nested Topics

```sql
-- Parent-child relationship
'parent:' || NEW.parent_id::text || ':child:' || NEW.id::text

-- Examples:
-- 'room:123:messages'
-- 'project:456:tasks'
```

### Pattern 3: User-Scoped Topics

```sql
-- User-specific channels
'user:' || NEW.user_id::text || ':notifications'

-- Examples:
-- 'user:abc-123:notifications'
-- 'user:abc-123:activity'
```

---

## Complete Example: Chat Messages

### Migration File

```sql
-- Enable realtime
ALTER PUBLICATION supabase_realtime ADD TABLE messages;

-- Create trigger function
CREATE OR REPLACE FUNCTION messages_broadcast_trigger()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
  PERFORM realtime.broadcast_changes(
    'room:' || COALESCE(NEW.room_id, OLD.room_id)::text || ':messages',
    TG_OP,
    TG_OP,
    TG_TABLE_NAME,
    TG_TABLE_SCHEMA,
    NEW,
    OLD
  );
  RETURN COALESCE(NEW, OLD);
END;
$$;

-- Create trigger
DROP TRIGGER IF EXISTS messages_broadcast ON messages;
CREATE TRIGGER messages_broadcast
  AFTER INSERT OR UPDATE OR DELETE ON messages
  FOR EACH ROW EXECUTE FUNCTION messages_broadcast_trigger();

-- RLS policies for realtime.messages
CREATE POLICY "room_members_can_receive_message_broadcasts" 
ON realtime.messages
FOR SELECT TO authenticated
USING (
  topic LIKE 'room:%:messages' AND
  EXISTS (
    SELECT 1 FROM room_members
    WHERE user_id = auth.uid()
    AND room_id = SPLIT_PART(topic, ':', 2)::bigint
  )
);

CREATE POLICY "room_members_can_send_message_broadcasts" 
ON realtime.messages
FOR INSERT TO authenticated
WITH CHECK (
  topic LIKE 'room:%:messages' AND
  EXISTS (
    SELECT 1 FROM room_members
    WHERE user_id = auth.uid()
    AND room_id = SPLIT_PART(topic, ':', 2)::bigint
  )
);

-- Performance index
CREATE INDEX IF NOT EXISTS idx_room_members_user_room
ON room_members(user_id, room_id);
```

---

## Conditional Broadcasting

Only broadcast significant changes:

```sql
CREATE OR REPLACE FUNCTION conditional_broadcast_trigger()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
  -- Only broadcast on status change
  IF TG_OP = 'UPDATE' AND OLD.status IS DISTINCT FROM NEW.status THEN
    PERFORM realtime.broadcast_changes(
      'item:' || NEW.id::text,
      TG_OP,
      'status_changed',  -- Custom event name
      TG_TABLE_NAME,
      TG_TABLE_SCHEMA,
      NEW,
      OLD
    );
  ELSIF TG_OP IN ('INSERT', 'DELETE') THEN
    PERFORM realtime.broadcast_changes(
      'item:' || COALESCE(NEW.id, OLD.id)::text,
      TG_OP,
      TG_OP,
      TG_TABLE_NAME,
      TG_TABLE_SCHEMA,
      NEW,
      OLD
    );
  END IF;
  
  RETURN COALESCE(NEW, OLD);
END;
$$;
```

---

## Custom Message Format

Use `realtime.send()` for completely custom messages:

```sql
CREATE OR REPLACE FUNCTION custom_notification_trigger()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
  PERFORM realtime.send(
    'user:' || NEW.user_id::text || ':notifications',  -- Topic
    'new_notification',                                  -- Event
    jsonb_build_object(                                 -- Custom payload
      'id', NEW.id,
      'title', NEW.title,
      'type', NEW.notification_type,
      'created_at', NEW.created_at
    ),
    false  -- Public channel (true = private)
  );
  RETURN NEW;
END;
$$;
```

---

## Testing the Trigger

### 1. Verify Trigger Exists

```sql
SELECT 
  trigger_name,
  event_manipulation,
  event_object_table,
  action_statement
FROM information_schema.triggers
WHERE trigger_name = 'your_table_broadcast';
```

### 2. Check Realtime Publication

```sql
SELECT * FROM pg_publication_tables 
WHERE pubname = 'supabase_realtime';
```

### 3. Test Manual Trigger

```sql
-- Insert test record
INSERT INTO your_table (name, user_id) 
VALUES ('Test', auth.uid());

-- Check realtime.messages table (messages expire after 3 days)
SELECT * FROM realtime.messages 
WHERE topic LIKE 'your_topic:%'
ORDER BY inserted_at DESC
LIMIT 10;
```

---

## Troubleshooting

### Trigger Not Firing

1. Verify trigger exists:
   ```sql
   SELECT * FROM pg_trigger WHERE tgname = 'your_table_broadcast';
   ```

2. Check function exists:
   ```sql
   SELECT * FROM pg_proc WHERE proname = 'your_table_broadcast_trigger';
   ```

3. Test trigger manually:
   ```sql
   INSERT INTO your_table (field) VALUES ('test');
   ```

### Messages Not Reaching Client

1. **Check RLS policies exist:**
   ```sql
   SELECT * FROM pg_policies WHERE tablename = 'messages';
   ```

2. **Verify client uses private channel:**
   ```typescript
   const channel = supabase.channel('topic:123', {
     config: { private: true }
   });
   ```

3. **Check client calls setAuth:**
   ```typescript
   await supabase.realtime.setAuth(session.access_token);
   ```

### Performance Issues

1. **Add indexes for RLS policies:**
   ```sql
   CREATE INDEX idx_table_user_id ON your_table(user_id, id);
   ```

2. **Limit broadcast scope:**
   - Use specific topics, not wildcards
   - Filter in trigger function when possible

3. **Monitor trigger performance:**
   ```sql
   SELECT * FROM pg_stat_user_functions 
   WHERE funcname LIKE '%broadcast%';
   ```

---

## Migration Pattern

```sql
-- Filename: YYYYMMDDHHMMSS_enable_table_realtime.sql

-- Enable realtime
ALTER PUBLICATION supabase_realtime ADD TABLE your_table;

-- Create trigger function
CREATE OR REPLACE FUNCTION your_table_broadcast_trigger()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
  PERFORM realtime.broadcast_changes(
    'your_topic:' || COALESCE(NEW.id, OLD.id)::text,
    TG_OP,
    TG_OP,
    TG_TABLE_NAME,
    TG_TABLE_SCHEMA,
    NEW,
    OLD
  );
  RETURN COALESCE(NEW, OLD);
END;
$$;

-- Create trigger
DROP TRIGGER IF EXISTS your_table_broadcast ON your_table;
CREATE TRIGGER your_table_broadcast
  AFTER INSERT OR UPDATE OR DELETE ON your_table
  FOR EACH ROW EXECUTE FUNCTION your_table_broadcast_trigger();

-- RLS policies
CREATE POLICY "users_can_receive_broadcasts" ON realtime.messages
FOR SELECT TO authenticated
USING (
  topic LIKE 'your_topic:%' AND
  EXISTS (
    SELECT 1 FROM your_table
    WHERE id = SPLIT_PART(topic, ':', 2)::bigint
    AND user_id = auth.uid()
  )
);

-- Performance index
CREATE INDEX IF NOT EXISTS idx_your_table_user_id 
ON your_table(user_id, id);
```

---

## References

- [Supabase Realtime Broadcast](https://supabase.com/docs/guides/realtime/broadcast)
- [PostgreSQL Triggers](https://www.postgresql.org/docs/current/trigger-definition.html)
- `.clinerules/supabase/database/realtime_guide.md` - Comprehensive realtime guide
- `.clinerules/ui/realtime-nextjs.md` - Client-side implementation
