# Collapsible Drawer Chat Pattern

**Purpose**: Standard implementation pattern for chat interfaces using shadcn Sheet component as a collapsible side drawer.

**Why Drawers**: 
- Non-intrusive UI that doesn't block main content
- Mobile-friendly with proper responsive behavior
- Maintains context of the page while chatting
- Can be opened/closed quickly

---

## Component Architecture

### Pattern: Drawer → Interface → Hook

```
ActorChatDrawer (Wrapper)
  ├── Sheet (shadcn component)
  ├── Actor Selection
  ├── Context Loader (optional)
  └── ActorChatInterface (Chat UI)
       └── useAgent (Hook)
            └── useStream (LangGraph SDK)
```

---

## Implementation Steps

### Step 1: Install Required Components

```bash
cd nextjs_
npx shadcn@latest add sheet
npx shadcn@latest add select
npx shadcn@latest add alert
```

### Step 2: Create Chat Interface Component

**File**: `components/chat-interface.tsx`

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Bot, Send, Loader2, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatInterfaceProps {
  // Your props here
}

export function ChatInterface(props: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [/* dependencies */]);

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        {/* Message list */}
      </ScrollArea>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="min-h-[60px] max-h-[120px] resize-none"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <Button type="submit" size="icon" disabled={!input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </form>
    </div>
  );
}
```

### Step 3: Create Drawer Wrapper Component

**File**: `components/chat-drawer.tsx`

```typescript
'use client';

import { useState } from 'react';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { MessageSquare } from 'lucide-react';
import { ChatInterface } from './chat-interface';

export function ChatDrawer() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button variant="outline">
          <MessageSquare className="h-4 w-4 mr-2" />
          Open Chat
        </Button>
      </SheetTrigger>

      <SheetContent side="right" className="w-[500px] flex flex-col p-0">
        <SheetHeader className="p-6 pb-4 border-b">
          <SheetTitle>Chat</SheetTitle>
          <SheetDescription>
            Have a conversation
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 overflow-hidden">
          <ChatInterface onClose={() => setIsOpen(false)} />
        </div>
      </SheetContent>
    </Sheet>
  );
}
```

---

## Key Design Principles

### 1. Fixed Width

```typescript
<SheetContent side="right" className="w-[500px]">
```

**Why**: Consistent UI, prevents content reflow, mobile-responsive via Sheet's built-in breakpoints.

### 2. Flex Column Layout

```typescript
className="flex flex-col p-0"
```

**Structure**:
- Header (fixed)
- Chat interface (flex-1, scrollable)
- Input (fixed)

### 3. Overflow Handling

```typescript
<div className="flex-1 overflow-hidden">
  <ChatInterface />  {/* Internal ScrollArea */}
</div>
```

**Why**: Prevents drawer from growing beyond viewport, keeps header/input fixed.

### 4. Auto-scroll Messages

```typescript
useEffect(() => {
  if (scrollRef.current) {
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }
}, [messages]);
```

**When**: New message added, loading state changes.

---

## Common Patterns

### Pattern: Entity Selection

For drawers that can chat with multiple entities:

```typescript
<SheetHeader className="p-6 pb-4 border-b">
  <SheetTitle>Chat</SheetTitle>
  <SheetDescription>Select who to talk to</SheetDescription>
  
  <div className="space-y-2 pt-4">
    <Select value={selectedId} onValueChange={setSelectedId}>
      <SelectTrigger>
        <SelectValue placeholder="Select..." />
      </SelectTrigger>
      <SelectContent>
        {entities.map(entity => (
          <SelectItem key={entity.id} value={entity.id}>
            {entity.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  </div>
</SheetHeader>
```

### Pattern: Context Loading

For loading additional context into chat:

```typescript
{selectedEntity && (
  <ContextLoader
    entityId={selectedEntity}
    onContextLoad={handleContextLoad}
  />
)}
```

### Pattern: Empty State

```typescript
{!selectedEntity ? (
  <div className="flex items-center justify-center h-full text-muted-foreground p-8 text-center">
    <p>Select an entity to start chatting</p>
  </div>
) : (
  <ChatInterface {...props} />
)}
```

---

## Styling Guidelines

### Colors

- **User messages**: `bg-primary text-primary-foreground`
- **Agent messages**: `bg-muted`
- **Icons**: `text-muted-foreground`

### Spacing

- **Drawer padding**: Remove top-level padding (`p-0`), add to sections
- **Header**: `p-6 pb-4 border-b`
- **Chat area**: `p-4`
- **Input area**: `p-4 border-t`

### Icons

Use lucide-react icons consistently:
- `MessageSquare` - Trigger button
- `Bot` - Agent avatar
- `User` - User avatar
- `Send` - Submit button
- `Loader2` - Loading indicator

---

## Mobile Considerations

Sheet component handles mobile automatically:
- Full-screen on mobile
- Slide from right on desktop
- Touch gestures supported

To customize mobile behavior:

```typescript
<Sheet>
  <SheetContent 
    side="right" 
    className="w-full sm:w-[500px]"  // Full width mobile, fixed desktop
  >
```

---

## Accessibility

Sheet component includes:
- Focus trap when open
- ESC key to close
- ARIA labels
- Keyboard navigation

Ensure you:
- Label form inputs
- Add alt text to avatars
- Use semantic HTML
- Test with screen readers

---

## Performance

### Optimize Re-renders

```typescript
// Memoize expensive computations
const sortedMessages = useMemo(() => 
  messages.sort((a, b) => a.timestamp - b.timestamp),
  [messages]
);

// Callback refs for dynamic content
const messagesEndRef = useCallback((node) => {
  node?.scrollIntoView({ behavior: 'smooth' });
}, []);
```

### Lazy Load History

```typescript
// Load recent messages initially
const [page, setPage] = useState(1);
const [hasMore, setHasMore] = useState(true);

// Load more on scroll to top
const handleScroll = (e) => {
  if (e.target.scrollTop === 0 && hasMore) {
    loadMoreMessages(page + 1);
  }
};
```

---

## Testing Checklist

- [ ] Drawer opens/closes correctly
- [ ] Messages display properly
- [ ] Auto-scroll works
- [ ] Input submits on Enter
- [ ] Shift+Enter creates new line
- [ ] Loading states display
- [ ] Empty states display
- [ ] Mobile responsive
- [ ] Keyboard navigation works
- [ ] Screen reader accessible

---

## Examples in Project

**Implementation**: `nextjs_/components/actor-chat-drawer.tsx`
- Multi-actor selection
- Scenario context loading
- Meta-chat vs simulation threads

---

Last Updated: 2025-01-19
