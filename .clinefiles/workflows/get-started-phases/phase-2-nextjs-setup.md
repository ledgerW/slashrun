# Phase 2: Next.js Application Setup [MANDATORY]

**Purpose:** Set up Next.js application with Supabase template and apply all critical fixes

**Prerequisites:**
- Phase 0: Requirements documented
- Phase 1: Supabase running with complete database

**References:**
- `.clinefiles/ui.md` - Tailwind CSS v3 configuration and UI guidelines

---

## Step 1: Create Next.js App with Supabase Template

```bash
npx create-next-app -e with-supabase nextjs_
cd nextjs_
```

This creates a pre-configured app with:
- Cookie-based authentication
- TypeScript support
- Tailwind CSS v3.4.18
- Supabase client setup

---

## Step 2: Fix Environment Variables [CRITICAL]

The template uses **incorrect** variable names. You MUST fix these.

### Create `.env.local`

```env
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-from-phase-1
```

**CRITICAL:** Use `ANON_KEY`, NOT `PUBLISHABLE_KEY`!

### Fix All Supabase Client Files

Update these 4 files to use `ANON_KEY`:

**`lib/supabase/client.ts`:**
```typescript
import { createBrowserClient } from "@supabase/ssr";

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!, // Fixed
  );
}
```

**`lib/supabase/server.ts`:**
```typescript
// Change PUBLISHABLE_KEY to ANON_KEY
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
```

**`lib/supabase/middleware.ts`:**
```typescript
// Change PUBLISHABLE_KEY to ANON_KEY
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
```

**`lib/utils.ts`:**
```typescript
export const hasEnvVars =
  process.env.NEXT_PUBLIC_SUPABASE_URL &&
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY; // Fixed
```

---

## Step 3: Fix Post-Login Routing [CRITICAL]

Default template redirects to wrong page. Fix it.

### Update Login Form

**`components/login-form.tsx`:**
```typescript
// Change redirect from /protected to your dashboard
router.push("/dashboard"); // or /dashboard/scenarios
```

### Create Dashboard Index

**`app/dashboard/page.tsx`:**
```typescript
import { redirect } from 'next/navigation';

export default function DashboardPage() {
  redirect('/dashboard/scenarios'); // Your main page
}
```

---

## Step 4: Fix Sidebar Navigation [CRITICAL]

### Change Collapsible Mode

**`components/app-sidebar.tsx`:**
```typescript
// Change from offcanvas to icon
<Sidebar collapsible="icon" {...props}>
```

### Add Next.js Link to Navigation

**`components/nav-main.tsx` and `components/nav-secondary.tsx`:**
```typescript
import Link from "next/link";

<SidebarMenuButton asChild>
  <Link href={item.url}>
    {item.icon && <item.icon />}
    <span>{item.title}</span>
  </Link>
</SidebarMenuButton>
```

---

## Step 5: Install Dependencies and Start

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Step 6: Test Authentication

1. Go to `/auth/sign-up`
2. Create test account
3. Verify redirect to dashboard
4. Check Supabase Studio for profile creation

---

## Phase 2 Completion Checklist

- [ ] Next.js app created
- [ ] Environment variables fixed (ANON_KEY)
- [ ] All 4 Supabase client files updated
- [ ] Login redirect fixed
- [ ] Dashboard index page created
- [ ] Sidebar collapsible mode fixed
- [ ] Navigation links use Next.js Link
- [ ] Dependencies installed
- [ ] Dev server runs without errors
- [ ] User signup works
- [ ] Profile auto-created on signup

---

## Next Phase

**Proceed to:** [Phase 3: Marketing & UI Foundation](./phase-3-marketing-and-ui.md)
