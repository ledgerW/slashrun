# Supabase UI Blocks Reference

Pre-built React components that integrate seamlessly with Supabase services. These blocks provide production-ready implementations for authentication, file uploads, realtime features, and more.

**Official Blocks Gallery:** [supabase.com/ui](https://supabase.com/ui)

---

## Prerequisites

Supabase UI blocks are built on top of shadcn/ui. Ensure shadcn/ui is set up in your project before adding Supabase UI blocks.

---

## Authentication Blocks

### Password Authentication
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/password-auth
```
[Preview](https://supabase.com/ui/blocks/password-auth) - Complete email/password authentication flow with sign-up, sign-in, and password reset.

**Features:**
- Email and password validation
- Password reset flow
- Remember me functionality
- Error handling
- Loading states

### Social Authentication
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/social-auth
```
[Preview](https://supabase.com/ui/blocks/social-auth) - Authentication with social providers (Google, GitHub, etc.).

**Includes:**
- Provider buttons (Google, GitHub, Facebook, etc.)
- OAuth flow handling
- Customizable provider list
- Consistent styling

### Magic Link Authentication
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/magic-link
```
[Preview](https://supabase.com/ui/blocks/magic-link) - Passwordless authentication via email magic links.

**Features:**
- Email input with validation
- Magic link request handling
- Success confirmation
- Resend functionality

---

## File Upload Blocks

### Dropzone
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/dropzone
```
[Preview](https://supabase.com/ui/blocks/dropzone) - Drag-and-drop file upload with Supabase Storage integration.

**Features:**
- Drag and drop support
- File type validation
- Size limit enforcement
- Upload progress tracking
- Preview for images
- Delete functionality
- Multiple file support

### Image Uploader
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/image-uploader
```
[Preview](https://supabase.com/ui/blocks/image-uploader) - Specialized image upload with cropping and resizing.

**Features:**
- Image preview
- Crop and resize
- Format conversion
- Optimization
- Direct Storage upload

### Avatar Upload
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/avatar-upload
```
[Preview](https://supabase.com/ui/blocks/avatar-upload) - User avatar upload with cropping.

**Features:**
- Circular crop area
- Image preview
- Upload to Supabase Storage
- Fallback avatar
- Delete option

---

## Realtime Blocks

### Realtime Cursor
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/realtime-cursor
```
[Preview](https://supabase.com/ui/blocks/realtime-cursor) - Display user cursors in real-time for collaborative features.

**Features:**
- Cursor position tracking
- User identification
- Smooth animations
- Color coding
- Multiple users support

### Realtime Avatar Stack
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/realtime-avatar-stack
```
[Preview](https://supabase.com/ui/blocks/realtime-avatar-stack) - Show active users with avatar stack (like Google Docs).

**Features:**
- Real-time presence tracking
- Avatar display
- User count
- Hover information
- Responsive layout

### Realtime Chat
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/realtime-chat
```
[Preview](https://supabase.com/ui/blocks/realtime-chat) - Complete chat interface with realtime messages.

**Features:**
- Message sending/receiving
- Real-time updates
- User identification
- Timestamps
- Auto-scroll to latest
- Typing indicators (optional)

---

## User Profile Blocks

### Current User Avatar
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/current-user-avatar
```
[Preview](https://supabase.com/ui/blocks/current-user-avatar) - Display current user's avatar with dropdown menu.

**Features:**
- User avatar display
- Dropdown menu
- Profile link
- Settings link
- Sign out button
- User info display

### User Profile Card
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/user-profile-card
```
[Preview](https://supabase.com/ui/blocks/user-profile-card) - Detailed user profile display with edit capabilities.

**Features:**
- Avatar display
- User information fields
- Edit mode
- Form validation
- Save functionality
- Supabase integration

---

## Database Blocks

### Data Table with Supabase
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/data-table-supabase
```
[Preview](https://supabase.com/ui/blocks/data-table-supabase) - Data table with Supabase query integration.

**Features:**
- Server-side pagination
- Sorting
- Filtering
- Row selection
- CRUD operations
- Optimistic updates

### Infinite Scroll List
```bash
npx shadcn@latest add https://supabase.com/ui/blocks/infinite-scroll
```
[Preview](https://supabase.com/ui/blocks/infinite-scroll) - Infinite scrolling list with Supabase pagination.

**Features:**
- Automatic loading on scroll
- Loading indicators
- Error handling
- Performance optimized
- Customizable item renderer

---

## Installation & Usage

### Install a Block

```bash
# General format
npx shadcn@latest add https://supabase.com/ui/blocks/[block-name]

# Example: Password auth
npx shadcn@latest add https://supabase.com/ui/blocks/password-auth
```

### Configuration

Most Supabase UI blocks require minimal configuration:

1. **Ensure Supabase client is configured** - Blocks use your existing Supabase client setup
2. **Set up environment variables** - `.env.local` should have Supabase URL and Anon Key
3. **Configure policies** - Ensure RLS policies allow the operations the blocks perform

### Customization

All blocks are fully customizable:

- Modify styling with Tailwind classes
- Update validation rules
- Add custom fields
- Extend functionality
- Replace Supabase client calls

---

## Common Use Cases

### Authentication Flow
```bash
# Complete auth setup
npx shadcn@latest add https://supabase.com/ui/blocks/password-auth
npx shadcn@latest add https://supabase.com/ui/blocks/social-auth
npx shadcn@latest add https://supabase.com/ui/blocks/current-user-avatar
```

### File Management
```bash
# File upload and management
npx shadcn@latest add https://supabase.com/ui/blocks/dropzone
npx shadcn@latest add https://supabase.com/ui/blocks/avatar-upload
```

### Collaborative Features
```bash
# Real-time collaboration
npx shadcn@latest add https://supabase.com/ui/blocks/realtime-cursor
npx shadcn@latest add https://supabase.com/ui/blocks/realtime-avatar-stack
npx shadcn@latest add https://supabase.com/ui/blocks/realtime-chat
```

### User Profile Management
```bash
# User profile setup
npx shadcn@latest add https://supabase.com/ui/blocks/current-user-avatar
npx shadcn@latest add https://supabase.com/ui/blocks/user-profile-card
npx shadcn@latest add https://supabase.com/ui/blocks/avatar-upload
```

---

## Integration Tips

### 1. Authentication Integration

After adding auth blocks, update your middleware and protected routes:

```typescript
// middleware.ts
import { createClient } from '@/lib/supabase/middleware'

export async function middleware(request: NextRequest) {
  const { supabase, response } = createClient(request)
  await supabase.auth.getSession()
  return response
}
```

### 2. Storage Configuration

For file upload blocks, ensure Storage buckets are created:

```sql
-- Create storage bucket
insert into storage.buckets (id, name, public)
values ('avatars', 'avatars', true);

-- Set up RLS policies
create policy "Avatar images are publicly accessible"
on storage.objects for select
to public
using (bucket_id = 'avatars');

create policy "Users can upload their own avatar"
on storage.objects for insert
to authenticated
with check (bucket_id = 'avatars' and auth.uid()::text = (storage.foldername(name))[1]);
```

### 3. Realtime Configuration

Enable realtime for tables used by realtime blocks:

```sql
-- Enable realtime on messages table
alter publication supabase_realtime add table messages;
```

---

## Resources

- **Browse All Blocks:** [supabase.com/ui](https://supabase.com/ui)
- **Supabase UI Documentation:** [supabase.com/ui/docs](https://supabase.com/ui/docs/getting-started/quickstart)
- **Blog Announcement:** [Supabase UI Library Blog Post](https://supabase.com/blog/supabase-ui-library)
- **Supabase Docs:** [supabase.com/docs](https://supabase.com/docs)
- **shadcn/ui Docs:** [ui.shadcn.com/docs](https://ui.shadcn.com/docs)

---

## Examples

### Example: Adding Authentication

```bash
# Install password auth block
npx shadcn@latest add https://supabase.com/ui/blocks/password-auth

# Use in your login page
import { PasswordAuth } from '@/components/blocks/password-auth'

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <PasswordAuth />
    </div>
  )
}
```

### Example: Adding File Upload

```bash
# Install dropzone block
npx shadcn@latest add https://supabase.com/ui/blocks/dropzone

# Use in your component
import { Dropzone } from '@/components/blocks/dropzone'

export default function UploadPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Upload Files</h1>
      <Dropzone
        bucket="uploads"
        path="user-files"
        accept="image/*,application/pdf"
        maxSize={5242880} // 5MB
      />
    </div>
  )
}
```

### Example: Adding Realtime Features

```bash
# Install realtime avatar stack
npx shadcn@latest add https://supabase.com/ui/blocks/realtime-avatar-stack

# Use in your app header
import { RealtimeAvatarStack } from '@/components/blocks/realtime-avatar-stack'

export default function AppHeader() {
  return (
    <header className="border-b">
      <div className="container flex items-center justify-between py-4">
        <h1>My App</h1>
        <RealtimeAvatarStack channel="app-presence" />
      </div>
    </header>
  )
}
