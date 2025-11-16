# Supabase Realtime in Next.js

**Client-side implementation patterns for real-time features**

---

## Critical: JWT Authentication Required

### The Issue

Realtime WebSocket connections **REQUIRE** a valid JWT token. Using a custom publishable key will cause authentication failures.

### ✅ Correct Setup

```env
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Get the correct `ANON_KEY`:
```bash
npx supabase status --output json | grep ANON_KEY
```

### ❌ Wrong Setup

```env
# DO NOT USE PUBLISHABLE_KEY for realtime!
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_xxxxx
```

**Symptoms:**
- WebSocket connection fails
- Console: `WebSocket connection to 'ws://127.0.0.1:54321/realtime/v1/websocket' failed`
- Logs: `MalformedJWT: The token provided is not a valid JWT`

**Fix:** Update `.env.local` with correct `ANON_KEY` and **restart dev server**

---

## React Implementation Pattern

### Complete Example: postgres_changes

```typescript
'use client';

import { useEffect, useState, useRef } from 'react';
import { createClient } from '@/lib/supabase/client';

interface Message {
  id: number;
  content: string;
  created_at: string;
  // ... other fields
}

export function RealtimeMessages({ roomId }: { roomId: number }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const supabaseRef = useRef(createClient());
  const channelRef = useRef<any>(null);

  useEffect(() => {
    loadMessages();

    // Prevent duplicate subscriptions
    if (channelRef.current?.state === 'subscribed') return;

    const setupRealtime = async () => {
      const supabase = supabaseRef.current;

      const channel = supabase
        .channel(`room_${roomId}_messages`)
        .on(
          'postgres_changes',
          {
            event: '*',  // Listen to INSERT, UPDATE, DELETE
            schema: 'public',
            table: 'messages',
            filter: `room_id=eq.${roomId}`
          },
          (payload) => {
            console.log('📨 Change received:', payload);
            loadMessages();  // Reload all messages
          }
        )
        .subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            console.log('✅ Subscribed to messages');
          } else if (status === 'CHANNEL_ERROR') {
            console.error('❌ Channel error');
          }
        });

      channelRef.current = channel;
    };

    setupRealtime();

    // Cleanup on unmount
    return () => {
      if (channelRef.current) {
        supabaseRef.current.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [roomId]);

  async function loadMessages() {
    const supabase = supabaseRef.current;
    const { data, error } = await supabase
      .from('messages')
      .select('*')
      .eq('room_id', roomId)
      .order('created_at', { ascending: true });

    if (error) {
      console.error('Error loading messages:', error);
    } else {
      setMessages(data || []);
    }
    setLoading(false);
  }

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {messages.map((msg) => (
        <div key={msg.id}>{msg.content}</div>
      ))}
    </div>
  );
}
```

---

## Best Practices

### 1. Use Refs for Stable References

```typescript
// ✅ Good - stable reference across renders
const supabaseRef = useRef(createClient());
const channelRef = useRef<any>(null);

// ❌ Bad - creates new client on every render
const supabase = createClient();
```

### 2. Prevent Duplicate Subscriptions

```typescript
// Check state before subscribing
if (channelRef.current?.state === 'subscribed') return;
```

### 3. Always Clean Up

```typescript
useEffect(() => {
  // Setup subscription...
  
  return () => {
    if (channelRef.current) {
      supabaseRef.current.removeChannel(channelRef.current);
      channelRef.current = null;
    }
  };
}, [dependencies]);
```

### 4. Handle All States

```typescript
.subscribe((status, err) => {
  if (status === 'SUBSCRIBED') {
    console.log('✅ Connected');
  } else if (status === 'CHANNEL_ERROR') {
    console.error('❌ Error:', err);
  } else if (status === 'TIMED_OUT') {
    console.warn('⏱️ Timed out');
  } else if (status === 'CLOSED') {
    console.log('🔌 Closed');
  }
})
```

### 5. Restart After Env Changes

Environment variables load at startup. **You MUST restart** `npm run dev` after changing `.env.local`.

---

## Troubleshooting

### WebSocket Connection Fails

**Check these in order:**

1. **Environment variable**
   ```bash
   # Verify you're using ANON_KEY
   cat geosim-platform/.env.local
   ```

2. **Restart dev server**
   ```bash
   # Stop current server (Ctrl+C)
   npm run dev
   ```

3. **Verify Supabase running**
   ```bash
   npx supabase status
   ```

4. **Check realtime container**
   ```bash
   docker ps | grep realtime
   ```

### Messages Don't Update

**Checklist:**

- [ ] Filter matches your data (`filter: 'room_id=eq.123'`)
- [ ] Console shows "✅ Subscribed"
- [ ] Table name matches exactly
- [ ] Schema is 'public'
- [ ] Check Supabase logs: `docker logs supabase_realtime_sim_test`

### Channel Already Subscribed

**Solution:** Check state before subscribing

```typescript
if (channelRef.current?.state === 'subscribed') return;
```

### Stale Data After Update

**Issue:** Using old Supabase client reference

**Solution:** Use refs consistently

```typescript
const supabaseRef = useRef(createClient());

// Always use: supabaseRef.current
// Never create new: createClient()
```

---

## Testing Checklist

Test your implementation:

- [ ] Environment uses correct `ANON_KEY` (JWT token)
- [ ] Dev server restarted after env changes
- [ ] Supabase running without errors
- [ ] WebSocket connects (check browser console)
- [ ] Console shows "✅ Subscribed"
- [ ] Create new record → appears without refresh
- [ ] Update record → updates without refresh
- [ ] Delete record → removes without refresh
- [ ] Multiple browser tabs receive updates
- [ ] No duplicate subscriptions (check state)
- [ ] Component unmount cleans up subscription

---

## When to Use What

### postgres_changes (Recommended)

**Use for:**
- Database-backed data
- Local development
- Simple setup
- Messages stored in tables

**Advantages:**
- Works immediately
- No server-side setup
- Direct database listening

**Limitations:**
- Single-threaded (can be slow with many clients)
- Only database changes

### broadcast (Advanced)

**Use for:**
- Production with many users
- Low-latency requirements
- Custom message formats
- Ephemeral messages

**Requires:**
- Database triggers (see `.clinefiles/supabase/database/realtime-broadcast-setup.md`)
- RLS policies
- More complex setup

**For most applications, start with `postgres_changes`.**

---

## References

- [Supabase Realtime Docs](https://supabase.com/docs/guides/realtime)
- [Next.js Realtime Chat](https://supabase.com/ui/docs/nextjs/realtime-chat)
- `.clinefiles/supabase/database/realtime-broadcast-setup.md` - Server-side setup
- `.clinefiles/supabase/database/realtime_guide.md` - Comprehensive guide
