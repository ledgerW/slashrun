# Phase 2: Frontend Implementation [IF NEEDED]

**Purpose:** Implement Next.js frontend changes for the new feature

**Prerequisites:**
- Phase 0 complete with approved FEATURE_PLAN.md
- Phase 1 complete if database changes needed
- SYSTEM_REFERENCE.md reviewed for UI patterns

**Execute this phase if:** Feature requires UI pages, components, forms, or navigation changes

**Skip this phase if:** Feature is backend-only

**References:**
- `.clinerules/ui/ui.md`
- `.clinerules/ui/shadcn-components.md`
- `.clinerules/ui/shadcn-blocks.md`

---

## Overview

Phase 2 implements frontend changes, ensuring:

1. **Pages Created** - Following Next.js 16 patterns
2. **Components Built** - Using shadcn/ui conventions
3. **Forms Implemented** - With validation and error handling
4. **Navigation Updated** - Sidebar and routing
5. **Loading States** - User feedback on async operations
6. **Error Handling** - Clear user messages

**All UI must follow existing project patterns and conventions.**

---

## Step 1: Review UI Design from FEATURE_PLAN.md

### Extract UI Requirements

From FEATURE_PLAN.md Section 4, identify:
- New pages needed
- New components needed
- Updated components
- Navigation changes
- Form specifications
- UI mockups

### Review Existing UI Patterns

**Open similar pages in codebase:**
```bash
# Find similar pages
ls -la geosim-platform/app/dashboard/*/page.tsx
```

**Study patterns:**
- How are pages structured?
- How are forms implemented?
- How are tables/cards displayed?
- How is navigation handled?

---

## Step 2: Create Page Components

### Next.js 16 Page Pattern

**Template for new page:**

```typescript
// app/dashboard/[feature]/page.tsx
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { Suspense } from 'react'
import { FeatureList } from '@/components/feature-list'

export default async function FeaturePage() {
  const supabase = await createClient()
  
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    return redirect('/auth/login')
  }

  return (
    <div className="flex-1 w-full flex flex-col gap-12">
      <div className="w-full">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Feature Name</h1>
          <Link href="/dashboard/feature/new">
            <Button>Create New</Button>
          </Link>
        </div>

        <Suspense fallback={<LoadingSkeleton />}>
          <FeatureList />
        </Suspense>
      </div>
    </div>
  )
}
```

### Dynamic Route Pages (Detail/Edit)

**Detail page with Promise unwrapping:**

```typescript
// app/dashboard/[feature]/[id]/page.tsx
import { createClient } from '@/lib/supabase/server'
import { notFound } from 'next/navigation'

export default async function FeatureDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  // CRITICAL: Unwrap params Promise (Next.js 16+)
  const { id } = await params
  
  const supabase = await createClient()
  
  const { data: item, error } = await supabase
    .from('table_name')
    .select('*')
    .eq('id', id)
    .single()

  if (error || !item) {
    notFound()
  }

  return (
    <div>
      <h1>{item.name}</h1>
      {/* Render item details */}
    </div>
  )
}
```

---

## Step 3: Create Form Components

### Form with Validation

**Using react-hook-form + zod:**

```typescript
// components/feature-form.tsx
'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { useState } from 'react'

// Match database schema exactly
const formSchema = z.object({
  name: z.string().min(3, 'Name must be at least 3 characters'),
  description: z.string().optional(),
  status: z.enum(['active', 'inactive', 'archived']),
})

type FormData = z.infer<typeof formSchema>

interface FeatureFormProps {
  initialData?: FormData & { id: string }
  mode: 'create' | 'edit'
}

export function FeatureForm({ initialData, mode }: FeatureFormProps) {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: initialData || {
      name: '',
      description: '',
      status: 'active',
    },
  })

  async function onSubmit(data: FormData) {
    setIsSubmitting(true)
    const supabase = createClient()

    try {
      if (mode === 'create') {
        const { error } = await supabase
          .from('table_name')
          .insert([data])

        if (error) throw error

        toast.success('Created successfully')
        router.push('/dashboard/feature')
      } else {
        const { error } = await supabase
          .from('table_name')
          .update(data)
          .eq('id', initialData?.id)

        if (error) throw error

        toast.success('Updated successfully')
        router.push(`/dashboard/feature/${initialData?.id}`)
      }
      
      router.refresh()
    } catch (error) {
      console.error('Form submission error:', error)
      toast.error(`Failed to ${mode === 'create' ? 'create' : 'update'}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="Enter name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea placeholder="Enter description" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Status</FormLabel>
              <FormControl>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                    <SelectItem value="archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex gap-4">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create' : 'Update'}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
        </div>
      </form>
    </Form>
  )
}
```

---

## Step 4: Display Data with Loading States

### List Component with Loading

```typescript
// components/feature-list.tsx
import { createClient } from '@/lib/supabase/server'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'

export async function FeatureList() {
  const supabase = await createClient()
  
  const { data: items, error } = await supabase
    .from('table_name')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    return <div className="text-destructive">Error loading data</div>
  }

  if (!items || items.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          No items yet. Create your first one to get started.
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => (
        <Link key={item.id} href={`/dashboard/feature/${item.id}`}>
          <Card className="hover:bg-accent transition-colors">
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle>{item.name}</CardTitle>
                <Badge>{item.status}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {item.description}
              </p>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  )
}

// Loading skeleton
export function LoadingSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <Card key={i} className="animate-pulse">
          <CardHeader>
            <div className="h-6 bg-muted rounded w-3/4" />
          </CardHeader>
          <CardContent>
            <div className="h-4 bg-muted rounded w-full mb-2" />
            <div className="h-4 bg-muted rounded w-2/3" />
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
```

---

## Step 5: Update Navigation

### Add to Sidebar

```typescript
// components/app-sidebar.tsx
import { /* existing imports */ } from '@/components/ui/sidebar'
import { FeatureIcon } from 'lucide-react' // Choose appropriate icon

// In NavMain items array, add:
{
  title: 'Feature Name',
  url: '/dashboard/feature',
  icon: FeatureIcon,
  items: [
    {
      title: 'All Items',
      url: '/dashboard/feature',
    },
    {
      title: 'Create New',
      url: '/dashboard/feature/new',
    },
  ],
},
```

---

## Step 6: Error Handling

### Error Boundary

```typescript
// app/dashboard/feature/error.tsx
'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Feature error:', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
      <h2 className="text-2xl font-bold">Something went wrong</h2>
      <p className="text-muted-foreground">
        {error.message || 'An error occurred while loading this page'}
      </p>
      <Button onClick={reset}>Try again</Button>
    </div>
  )
}
```

---

## Step 7: Delete Functionality

### Delete with Confirmation

```typescript
// components/delete-feature-button.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { toast } from 'sonner'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Trash2 } from 'lucide-react'

interface DeleteFeatureButtonProps {
  id: string
  name: string
}

export function DeleteFeatureButton({ id, name }: DeleteFeatureButtonProps) {
  const router = useRouter()
  const [isDeleting, setIsDeleting] = useState(false)

  async function handleDelete() {
    setIsDeleting(true)
    const supabase = createClient()

    try {
      const { error } = await supabase
        .from('table_name')
        .delete()
        .eq('id', id)

      if (error) throw error

      toast.success('Deleted successfully')
      router.push('/dashboard/feature')
      router.refresh()
    } catch (error) {
      console.error('Delete error:', error)
      toast.error('Failed to delete')
      setIsDeleting(false)
    }
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive" size="sm" disabled={isDeleting}>
          <Trash2 className="h-4 w-4 mr-2" />
          Delete
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently delete "{name}". This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleDelete} disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

---

## Common Issues and Solutions

### Issue 1: Params not unwrapping (Next.js 16)

**Error:** `params.id is Promise {<pending>}`

**Solution:**
```typescript
// ❌ WRONG
const { id } = params

// ✅ CORRECT
const { id } = await params
```

### Issue 2: Form field names don't match database

**Error:** Data not saving or validation errors

**Solution:** Check database schema, ensure exact match including snake_case vs camelCase

### Issue 3: RLS blocking data fetch

**Error:** Empty data or "permission denied"

**Solution:** Verify user is authenticated and RLS policies allow SELECT

---

## Phase 2 Completion Checklist

- [ ] All new pages created
- [ ] Forms implemented with validation
- [ ] Loading states on all async operations
- [ ] Error handling with user-friendly messages
- [ ] Navigation updated in sidebar
- [ ] Delete functionality with confirmation
- [ ] Follows existing UI patterns
- [ ] TypeScript types correct
- [ ] No console errors

---

## Next Phase

**Proceed to:** 
- If agent changes needed: [Phase 3: Agent Integration](./phase-3-agent-integration.md)
- If multiple services touched: [Phase 4: Integration Testing](./phase-4-integration-testing.md)
- Otherwise: [Phase 5: Documentation Update](./phase-5-documentation-update.md)
