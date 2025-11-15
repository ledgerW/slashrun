# Phase 4: CRUD Implementation [MANDATORY]

**Purpose:** Implement appropriate data management for ALL entities based on their type

**Prerequisites:**
- Phase 3: UI foundation complete
- Phase 0: Entity classification complete (Primary, Junction, System-Generated, Configuration)

**References:**
- `.clinerules/ui/shadcn-blocks.md`
- `.clinerules/supabase/database/create_rls_policies.md`
- `PROJECT_REQUIREMENTS.md` - Reference throughout to ensure all entities are implemented

---

## Overview: Entity Types Require Different UIs

Not all entities need full CRUD forms. Implement the appropriate interface for each entity type:

| Entity Type | CRUD Approach | Example |
|-------------|---------------|---------|
| **Primary/Core** | Full CRUD with dedicated forms | Scenarios, Actors, Projects, Tasks |
| **Junction/Association** | Managed in parent entity forms | scenario_actors, project_members |
| **System-Generated** | Read-only display + optional delete | actor_messages, audit_logs, notifications |
| **Configuration/Reference** | Minimal admin CRUD | categories, types, status_options |

**Refer to PROJECT_REQUIREMENTS.md** to confirm which entities fall into which category.

---

## Critical: Display ALL Data (Including Relationships)

**Before creating new records, users must see existing data!**

This includes:
- Seed data from Phase 1
- Related entity data (not just IDs)
- Association counts and lists
- System-generated data

## Step 1: Implement Full CRUD for Primary Entities [MANDATORY]

For each **Primary/Core Entity** from Phase 0 (e.g., Scenarios, Actors, Projects, Tasks):

### Substep 1.1: Display Seed Data

Replace placeholder pages with data fetching to show existing records.

**`app/dashboard/[entity]/page.tsx`:**
```typescript
import { createClient } from '@/lib/supabase/server';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import Link from 'next/link';

export default async function EntityListPage() {
  const supabase = await createClient();
  
  // Fetch ALL entities for current user
  const { data: entities, error } = await supabase
    .from('entity_table')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    return <div>Error loading data: {error.message}</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Entities</h1>
        <Button asChild>
          <Link href="/dashboard/entity/new">
            <Plus className="mr-2 h-4 w-4" />
            Create New
          </Link>
        </Button>
      </div>

      {entities && entities.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {entities.map((entity) => (
            <Card key={entity.id}>
              <CardHeader>
                <CardTitle>{entity.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                  {entity.description}
                </p>
                <div className="flex gap-2">
                  <Button asChild size="sm" variant="outline">
                    <Link href={`/dashboard/entity/${entity.id}`}>View</Link>
                  </Button>
                  <Button asChild size="sm" variant="outline">
                    <Link href={`/dashboard/entity/${entity.id}/edit`}>Edit</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              No entities yet. Create your first one!
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

**Verify:** Seed data from Phase 1 should be visible immediately!

### Substep 1.2: Create Operations

Implement forms for users to create new records.

### Form Component

**`components/entity-form.tsx`:**
```typescript
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

const formSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  description: z.string().optional(),
});

type EntityFormValues = z.infer<typeof formSchema>;

export function EntityForm({ entity }: { entity?: any }) {
  const router = useRouter();
  const supabase = createClient();
  
  const form = useForm<EntityFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: entity?.name || '',
      description: entity?.description || '',
    },
  });

  async function onSubmit(values: EntityFormValues) {
    try {
      if (entity) {
        // UPDATE
        const { error } = await supabase
          .from('entity_table')
          .update(values)
          .eq('id', entity.id);

        if (error) throw error;
        toast.success('Updated successfully');
      } else {
        // CREATE
        const { error } = await supabase
          .from('entity_table')
          .insert([values]);

        if (error) throw error;
        toast.success('Created successfully');
      }
      
      router.push('/dashboard/entity');
      router.refresh();
    } catch (error) {
      toast.error('Operation failed');
      console.error(error);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input {...field} />
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
                <Textarea {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <div className="flex gap-2">
          <Button type="submit">
            {entity ? 'Update' : 'Create'}
          </Button>
          <Button 
            type="button" 
            variant="outline"
            onClick={() => router.back()}
          >
            Cancel
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

### New Page

**`app/dashboard/[entity]/new/page.tsx`:**
```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EntityForm } from '@/components/entity-form';

export default function NewEntityPage() {
  return (
    <div className="max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Create New Entity</CardTitle>
        </CardHeader>
        <CardContent>
          <EntityForm />
        </CardContent>
      </Card>
    </div>
  );
}
```

### Substep 1.3: Read Operations - Detail Pages

Create dedicated detail/view pages for each entity.

**`app/dashboard/[entity]/[id]/page.tsx`:**
```typescript
import { createClient } from '@/lib/supabase/server';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DeleteButton } from '@/components/delete-button';
import Link from 'next/link';
import { notFound } from 'next/navigation';

export default async function EntityDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const supabase = await createClient();
  
  const { data: entity, error } = await supabase
    .from('entity_table')
    .select('*')
    .eq('id', params.id)
    .single();

  if (error || !entity) {
    notFound();
  }

  return (
    <div className="space-y-4 max-w-2xl">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">{entity.name}</h1>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link href={`/dashboard/entity/${entity.id}/edit`}>Edit</Link>
          </Button>
          <DeleteButton entityId={entity.id} />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="space-y-2">
            <div>
              <dt className="font-semibold">Description</dt>
              <dd className="text-muted-foreground">
                {entity.description || 'No description'}
              </dd>
            </div>
            <div>
              <dt className="font-semibold">Created</dt>
              <dd className="text-muted-foreground">
                {new Date(entity.created_at).toLocaleDateString()}
              </dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Substep 1.4: Update Operations - Edit Pages

Implement edit functionality reusing the form component.

**`app/dashboard/[entity]/[id]/edit/page.tsx`:**
```typescript
import { createClient } from '@/lib/supabase/server';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EntityForm } from '@/components/entity-form';
import { notFound } from 'next/navigation';

export default async function EditEntityPage({
  params,
}: {
  params: { id: string };
}) {
  const supabase = await createClient();
  
  const { data: entity, error } = await supabase
    .from('entity_table')
    .select('*')
    .eq('id', params.id)
    .single();

  if (error || !entity) {
    notFound();
  }

  return (
    <div className="max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Edit Entity</CardTitle>
        </CardHeader>
        <CardContent>
          <EntityForm entity={entity} />
        </CardContent>
      </Card>
    </div>
  );
}
```

### Substep 1.5: Delete Operations

Add safe deletion with confirmation dialogs.

**`components/delete-button.tsx`:**
```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
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
} from '@/components/ui/alert-dialog';
import { createClient } from '@/lib/supabase/client';
import { toast } from 'sonner';
import { Trash2 } from 'lucide-react';

export function DeleteButton({ entityId }: { entityId: string }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();
  const supabase = createClient();

  async function handleDelete() {
    setIsDeleting(true);
    try {
      const { error } = await supabase
        .from('entity_table')
        .delete()
        .eq('id', entityId);

      if (error) throw error;

      toast.success('Deleted successfully');
      router.push('/dashboard/entity');
      router.refresh();
    } catch (error) {
      toast.error('Delete failed');
      console.error(error);
      setIsDeleting(false);
    }
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">
          <Trash2 className="mr-2 h-4 w-4" />
          Delete
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            disabled={isDeleting}
            className="bg-destructive text-destructive-foreground"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
```

---

## Step 2: Implement Association Management for Junction Tables [MANDATORY]

For each **Junction/Association Table** from Phase 0 (e.g., scenario_actors, project_members, post_tags):

**DO NOT create standalone CRUD pages for these tables.**

Instead, manage associations within the parent entity's interface:

### Approach 1: Multi-Select in Form

Add association UI to create/edit forms:

```typescript
// In scenario form component
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

// Fetch available actors
const { data: actors } = await supabase.from('actors').select('id, name');

// In form schema
const formSchema = z.object({
  name: z.string().min(2),
  description: z.string().optional(),
  actor_ids: z.array(z.number()).optional(), // For junction table
});

// In form
<FormField
  control={form.control}
  name="actor_ids"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Actors</FormLabel>
      <FormControl>
        <MultiSelect
          options={actors?.map(a => ({ label: a.name, value: a.id })) || []}
          value={field.value || []}
          onChange={field.onChange}
        />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>

// In submit handler
async function onSubmit(values: FormValues) {
  // 1. Create/update main entity
  const { data: scenario, error } = await supabase
    .from('scenarios')
    .insert([{ name: values.name, description: values.description }])
    .select()
    .single();
  
  if (error) throw error;
  
  // 2. Create junction table entries
  if (values.actor_ids && values.actor_ids.length > 0) {
    const junctionEntries = values.actor_ids.map(actor_id => ({
      scenario_id: scenario.id,
      actor_id,
    }));
    
    await supabase.from('scenario_actors').insert(junctionEntries);
  }
  
  toast.success('Created successfully');
  router.push('/dashboard/scenarios');
}
```

### Approach 2: Add/Remove List in Detail Page

Display and manage associations in the entity's detail view:

```typescript
// In scenario detail page
export default async function ScenarioDetailPage({ params }: { params: { id: string } }) {
  const supabase = await createClient();
  
  // Fetch scenario with associated actors
  const { data: scenario } = await supabase
    .from('scenarios')
    .select(`
      *,
      scenario_actors (
        actor:actors (
          id,
          name,
          type
        )
      )
    `)
    .eq('id', params.id)
    .single();

  return (
    <div className="space-y-6">
      <h1>{scenario.name}</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Actors in this Scenario</CardTitle>
        </CardHeader>
        <CardContent>
          {scenario.scenario_actors.length > 0 ? (
            <ul className="space-y-2">
              {scenario.scenario_actors.map(({ actor }) => (
                <li key={actor.id} className="flex justify-between items-center">
                  <Link href={`/dashboard/actors/${actor.id}`}>
                    {actor.name} ({actor.type})
                  </Link>
                  <RemoveActorButton 
                    scenarioId={scenario.id} 
                    actorId={actor.id} 
                  />
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No actors yet</p>
          )}
          <AddActorButton scenarioId={scenario.id} />
        </CardContent>
      </Card>
    </div>
  );
}
```

**Key Point:** Junction tables are managed through parent entity UIs, not separate CRUD pages.

---

## Step 3: Display System-Generated Data [MANDATORY]

For each **System-Generated Table** from Phase 0 (e.g., actor_messages, audit_logs, notifications):

**DO NOT create Create/Edit forms for these tables.**

These records are created automatically by the application. Implement read-only views:

### Example: Actor Messages (Created During Simulation)

```typescript
// In actor detail page or scenario detail page
export default async function ActorDetailPage({ params }: { params: { id: string } }) {
  const supabase = await createClient();
  
  // Fetch actor
  const { data: actor } = await supabase
    .from('actors')
    .select('*')
    .eq('id', params.id)
    .single();
  
  // Fetch messages (read-only)
  const { data: messages } = await supabase
    .from('actor_messages')
    .select(`
      *,
      sender:sender_actor_id (name),
      recipient:recipient_actor_id (name)
    `)
    .or(`sender_actor_id.eq.${params.id},recipient_actor_id.eq.${params.id}`)
    .order('created_at', { ascending: false })
    .limit(50);

  return (
    <div className="space-y-6">
      <h1>{actor.name}</h1>
      
      <Card>
        <CardHeader className="flex flex-row justify-between items-center">
          <CardTitle>Message History</CardTitle>
          <ClearMessagesButton actorId={actor.id} />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {messages?.map(msg => (
              <div key={msg.id} className="border-l-2 pl-4">
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>{msg.sender.name} → {msg.recipient?.name || 'All'}</span>
                  <span>{new Date(msg.created_at).toLocaleString()}</span>
                </div>
                <p className="mt-1">{msg.content}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Optional: Clear/delete button
'use client';
export function ClearMessagesButton({ actorId }: { actorId: number }) {
  async function clearMessages() {
    const supabase = createClient();
    await supabase
      .from('actor_messages')
      .delete()
      .or(`sender_actor_id.eq.${actorId},recipient_actor_id.eq.${actorId}`);
    
    toast.success('Messages cleared');
    router.refresh();
  }
  
  return <Button onClick={clearMessages} variant="outline">Clear History</Button>;
}
```

**Key Point:** System-generated data is displayed but not created through forms. Users can view and optionally delete/manage, but not create or edit.

---

## Step 4: Display ALL Relationship Data [MANDATORY]

For EVERY foreign key and relationship in your schema, you must display related entity data, not just IDs.

### Rule 1: Never Display Raw IDs

❌ **WRONG:**
```typescript
<p>Created by: {scenario.user_id}</p>
<p>Actor: {message.sender_actor_id}</p>
```

✅ **CORRECT:**
```typescript
// Fetch with joins
const { data: scenario } = await supabase
  .from('scenarios')
  .select(`
    *,
    profile:profiles!user_id (full_name)
  `)
  .eq('id', id)
  .single();

<p>Created by: {scenario.profile.full_name}</p>

// Or fetch related entity names
const { data: message } = await supabase
  .from('actor_messages')
  .select(`
    *,
    sender:actors!sender_actor_id (name),
    recipient:actors!recipient_actor_id (name)
  `)
  .eq('id', id)
  .single();

<p>{message.sender.name} → {message.recipient.name}</p>
```

### Rule 2: One-to-Many - Show Related Entities

**Parent Entity:** Show count and list of children

```typescript
// In project detail page
const { data: project } = await supabase
  .from('projects')
  .select(`
    *,
    tasks (id, name, status)
  `)
  .eq('id', params.id)
  .single();

return (
  <Card>
    <CardHeader>
      <CardTitle>Tasks ({project.tasks.length})</CardTitle>
    </CardHeader>
    <CardContent>
      <ul>
        {project.tasks.map(task => (
          <li key={task.id}>
            <Link href={`/dashboard/tasks/${task.id}`}>
              {task.name} - {task.status}
            </Link>
          </li>
        ))}
      </ul>
    </CardContent>
  </Card>
);
```

**Child Entity:** Show parent with link

```typescript
// In task detail page
const { data: task } = await supabase
  .from('tasks')
  .select(`
    *,
    project:projects (id, name)
  `)
  .eq('id', params.id)
  .single();

return (
  <div>
    <p className="text-muted-foreground">
      Project: <Link href={`/dashboard/projects/${task.project.id}`}>
        {task.project.name}
      </Link>
    </p>
  </div>
);
```

### Rule 3: Many-to-Many - Show Both Sides

**Both entities should show associated entities:**

```typescript
// In scenario detail - show actors
const { data: scenario } = await supabase
  .from('scenarios')
  .select(`
    *,
    scenario_actors (
      actor:actors (id, name, type)
    )
  `)
  .eq('id', params.id)
  .single();

<p>Actors: {scenario.scenario_actors.length}</p>
<ul>
  {scenario.scenario_actors.map(({ actor }) => (
    <li key={actor.id}>
      <Link href={`/dashboard/actors/${actor.id}`}>
        {actor.name}
      </Link>
    </li>
  ))}
</ul>

// In actor detail - show scenarios
const { data: actor } = await supabase
  .from('actors')
  .select(`
    *,
    scenario_actors (
      scenario:scenarios (id, name, status)
    )
  `)
  .eq('id', params.id)
  .single();

<p>Used in {actor.scenario_actors.length} scenarios</p>
<ul>
  {actor.scenario_actors.map(({ scenario }) => (
    <li key={scenario.id}>
      <Link href={`/dashboard/scenarios/${scenario.id}`}>
        {scenario.name}
      </Link>
    </li>
  ))}
</ul>
```

### Rule 4: Make Relationships Navigable

All related entity names should be clickable links to navigate to that entity's detail page.

```typescript
<Link 
  href={`/dashboard/${entity_type}/${entity.id}`}
  className="text-primary hover:underline"
>
  {entity.name}
</Link>
```

---

## Step 5: Add Toast Notifications [MANDATORY]

Install and configure toast notifications for user feedback:

```bash
npx shadcn@latest add sonner
```

**`app/layout.tsx`:**
```typescript
import { Toaster } from '@/components/ui/sonner';

// In body
<Toaster />
```

Use in all operations:
```typescript
import { toast } from 'sonner';

toast.success('Created successfully');
toast.error('Operation failed');
toast.info('Processing...');
```

---

## Phase 4 Completion Checklist

Before proceeding to Phase 5, verify against **PROJECT_REQUIREMENTS.md**:

### Primary Entities (Full CRUD)
For each primary entity:
- [ ] List page displays seed data in table or cards
- [ ] Create form working with validation
- [ ] Detail page working with all fields
- [ ] Edit form working (reuses create form)
- [ ] Delete with confirmation dialog
- [ ] Toast notifications on all operations
- [ ] Error handling with user feedback
- [ ] Loading states on async operations

### Junction/Association Tables
For each junction table:
- [ ] Identified which parent entity manages it
- [ ] Association UI added to parent forms or detail pages
- [ ] Can add associations through parent entity
- [ ] Can remove associations through parent entity
- [ ] Associated entities displayed in both parent entities
- [ ] No standalone CRUD pages for junction tables

### System-Generated Data
For each system-generated table:
- [ ] Read-only display implemented
- [ ] Data shown in appropriate context (detail pages, timelines, etc.)
- [ ] Optional delete/clear functionality if needed
- [ ] No create or edit forms
- [ ] Clear labeling that data is system-generated

### Relationship Data Display
- [ ] No raw IDs displayed anywhere in UI
- [ ] All foreign keys show related entity names
- [ ] Related entity names are clickable links
- [ ] One-to-many: Parent shows children list with count
- [ ] One-to-many: Child shows parent with link
- [ ] Many-to-many: Both sides show associations
- [ ] Navigation between related entities works

### General Requirements
- [ ] All seed data from Phase 1 is visible
- [ ] Toast notifications configured (Sonner)
- [ ] All forms validate input
- [ ] All operations handle errors gracefully
- [ ] Loading states visible during async operations
- [ ] Empty states shown when no data exists

### Cross-Reference PROJECT_REQUIREMENTS.md
- [ ] Count all entities in requirements document
- [ ] Verify appropriate UI exists for each entity type
- [ ] Confirm all relationships are displayed
- [ ] Verify all features marked "CRUD" are implemented

**Cannot proceed to Phase 5 until all items are verified ✓**

---

## Next Phase

**Proceed to:** [Phase 5: User Management](./phase-5-user-management.md)

**With:** Complete data management for all entities and full relationship visibility
