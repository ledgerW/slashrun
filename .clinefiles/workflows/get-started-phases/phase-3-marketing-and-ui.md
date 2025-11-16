# Phase 3: Marketing & UI Foundation [MANDATORY]

**Purpose:** Build complete UI foundation including landing page and dashboard

**Prerequisites:**
- Phase 2: Next.js app running

**References:**
- `.clinefiles/ui.md`
- `.clinefiles/ui/shadcn-blocks.md`
- `.clinefiles/ui/shadcn-components.md`

---

## Phase 3.0: Marketing/Landing Page [MANDATORY]

Every application needs a professional landing page.

### Install Landing Page Components

```bash
# Core components
npx shadcn@latest add button badge card separator

# Navigation
npx shadcn@latest add navigation-menu
```

### Create Marketing Layout

**`app/(marketing)/layout.tsx`:**
```typescript
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold">YourApp</span>
          </Link>
          
          <nav className="flex items-center space-x-6">
            <Link href="#features">Features</Link>
            <Link href="#pricing">Pricing</Link>
            <Button variant="ghost" asChild>
              <Link href="/auth/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/auth/sign-up">Get Started</Link>
            </Button>
          </nav>
        </div>
      </header>
      
      <main className="flex-1">{children}</main>
      
      <footer className="border-t py-6">
        <div className="container">
          <p className="text-center text-sm text-muted-foreground">
            © 2025 YourApp. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
```

### Create Landing Page

**`app/(marketing)/page.tsx`:**

Use requirements from Phase 0 to build:
- **Hero Section** - Headline, subheadline, CTA, visual
- **Features Section** - 3-6 key features with icons
- **Pricing Section** - 3 tiers (Free, Pro, Enterprise)
- **Final CTA** - Strong call-to-action

See `.clinefiles/ui/shadcn-blocks.md` for block examples.

---

## Phase 3.1: Dashboard Installation [MANDATORY]

```bash
npx shadcn@latest add https://ui.shadcn.com/r/styles/default/dashboard-01.json
```

This installs:
- AppSidebar
- SiteHeader  
- Layout components

### Configure Sidebar Navigation

**`components/app-sidebar.tsx`:**

Update navigation items to match your entities:
```typescript
const navItems = [
  { title: "Dashboard", url: "/dashboard", icon: Home },
  { title: "Entity1", url: "/dashboard/entity1", icon: Icon1 },
  { title: "Entity2", url: "/dashboard/entity2", icon: Icon2 },
  { title: "Entity3", url: "/dashboard/entity3", icon: Icon3 },
  { title: "Settings", url: "/dashboard/settings", icon: Settings },
];
```

---

## Phase 3.2: Core UI Components [MANDATORY]

Install components needed for CRUD operations:

```bash
# Forms
npx shadcn@latest add form input textarea select checkbox

# Data display
npx shadcn@latest add card badge table

# Overlays
npx shadcn@latest add dialog alert-dialog sheet

# Feedback
npx shadcn@latest add sonner toast alert
```

---

## Phase 3.3: Create Placeholder Pages [MANDATORY]

**All menu items MUST have working pages.**

For each entity, create:
```
app/dashboard/[entity]/
├── page.tsx           # List view
├── [id]/
│   ├── page.tsx      # Detail view
│   └── edit/
│       └── page.tsx  # Edit form
└── new/
    └── page.tsx      # Create form
```

**Basic placeholder:**
```typescript
export default function EntityPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold">Entity Name</h1>
      <p>Content coming in Phase 4</p>
    </div>
  );
}
```

### Settings Page Placeholder

```bash
npx shadcn@latest add https://ui.shadcn.com/r/styles/default/settings-01.json
```

Customize for user settings (Phase 5).

---

## Phase 3 Completion Checklist

- [ ] Landing page with hero section
- [ ] Landing page with features section  
- [ ] Landing page with pricing section
- [ ] Landing page with final CTA
- [ ] Dashboard block installed
- [ ] Sidebar navigation configured
- [ ] All core UI components installed
- [ ] ALL menu items have working pages (no 404s)
- [ ] Settings page created
- [ ] Navigation verified working

---

## Next Phase

**Proceed to:** [Phase 4: CRUD Implementation](./phase-4-crud-implementation.md)
