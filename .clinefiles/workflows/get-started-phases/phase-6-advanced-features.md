# Phase 6: Advanced Features [MANDATORY]

**Purpose:** Implement advanced features based on application needs

**Prerequisites:**
- Phase 5: User management complete

**References:**
- `.clinefiles/ui/reactflow-patterns.md`
- `.clinefiles/supabase/realtime_guide.md`

---

## ReactFlow Integration Decision [CRITICAL]

**Determine if ReactFlow is needed based on Phase 0 requirements.**

### ReactFlow is MANDATORY if application includes:

✅ **Workflow Designers**
- Building automation workflows
- Creating multi-step processes
- Designing approval chains

✅ **Mind Maps / Concept Mapping**
- Visual brainstorming tools
- Knowledge organization

✅ **System Architecture Diagrams**
- Infrastructure visualization
- Service dependency maps

✅ **Data Flow Visualizations**
- ETL pipeline designers
- Data transformation workflows

✅ **Decision Trees**
- Rule-based logic builders
- Conditional path visualization

✅ **Node-Based Editors**
- Visual programming interfaces
- Graph-based data structures

### ReactFlow NOT needed for:
❌ Simple CRUD applications
❌ List/table-based interfaces
❌ Form-based data entry
❌ Standard dashboards

---

## ReactFlow Implementation [IF APPLICABLE]

**If ReactFlow is needed, it is MANDATORY to implement.**

### Install ReactFlow

```bash
npm install @xyflow/react
```

### Basic Flow Component

**Reference:** `.clinefiles/ui/reactflow-patterns.md` for complete patterns

**`components/flow-editor.tsx`:**
```typescript
'use client';

import { useState, useCallback } from 'react';
import {
  ReactFlow,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  type Node,
  type Edge,
  type NodeChange,
  type EdgeChange,
  type Connection,
  Background,
  Controls,
  MiniMap,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export default function FlowEditor({
  initialNodes,
  initialEdges,
}: {
  initialNodes: Node[];
  initialEdges: Edge[];
}) {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
```

### Save/Load with Supabase

**`lib/flow-storage.ts`:**
```typescript
import { createClient } from '@/lib/supabase/client';
import type { Node, Edge } from '@xyflow/react';

export async function saveFlow(
  flowId: string,
  nodes: Node[],
  edges: Edge[]
) {
  const supabase = createClient();
  
  const { error } = await supabase
    .from('flows')
    .upsert({
      id: flowId,
      nodes: JSON.stringify(nodes),
      edges: JSON.stringify(edges),
      updated_at: new Date().toISOString(),
    });

  return { error };
}

export async function loadFlow(flowId: string) {
  const supabase = createClient();
  
  const { data, error } = await supabase
    .from('flows')
    .select('nodes, edges')
    .eq('id', flowId)
    .single();

  if (error || !data) return null;

  return {
    nodes: JSON.parse(data.nodes) as Node[],
    edges: JSON.parse(data.edges) as Edge[],
  };
}
```

**See `.clinefiles/ui/reactflow-patterns.md` for:**
- Custom node types
- Drag-and-drop functionality
- Autosave implementation
- Advanced patterns

---

## Real-time Features [IF APPLICABLE]

**If application needs real-time features, implement using Supabase Realtime.**

**Reference:** `.clinefiles/supabase/realtime_guide.md`

### Basic Realtime Subscription

```typescript
'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';

export default function RealtimeComponent() {
  const [data, setData] = useState([]);
  const supabase = createClient();

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Subscribe to changes
    const channel = supabase
      .channel('table-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'your_table'
        },
        (payload) => {
          // Handle real-time updates
          fetchData();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  async function fetchData() {
    const { data } = await supabase
      .from('your_table')
      .select('*');
    setData(data || []);
  }

  return <div>{/* Render data */}</div>;
}
```

---

## File Uploads [IF APPLICABLE]

**If application handles file uploads:**

### Install Upload Components

```bash
npx shadcn@latest add https://supabase.com/ui/blocks/dropzone
```

### Basic File Upload

```typescript
'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

export function FileUpload() {
  const [uploading, setUploading] = useState(false);
  const supabase = createClient();

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const fileExt = file.name.split('.').pop();
      const fileName = `${Math.random()}.${fileExt}`;
      
      const { error } = await supabase.storage
        .from('uploads')
        .upload(fileName, file);

      if (error) throw error;
      
      toast.success('File uploaded successfully');
    } catch (error) {
      toast.error('Upload failed');
      console.error(error);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <Input
        type="file"
        onChange={handleUpload}
        disabled={uploading}
      />
    </div>
  );
}
```

---

## Analytics/Charts [IF APPLICABLE]

**If application needs data visualization:**

```bash
npx shadcn@latest add chart
```

**See:** [ui.shadcn.com/charts](https://ui.shadcn.com/charts) for examples

---

## Billing & Payments (Stripe) [IF APPLICABLE]

**If application requires subscription billing or payment processing:**

### Decision Criteria

Stripe integration is needed if your application:
- ✅ Requires subscription billing (monthly/annual plans)
- ✅ Sells one-time products or services
- ✅ Needs tiered pricing (Free/Pro/Enterprise)
- ✅ Requires feature gating based on subscription level
- ✅ Needs customer self-service billing portal

### Implementation Steps

**See: `.clinefiles/stripe/stripe-integration.md` for complete guide**

#### Step 1: Stripe Account Setup

1. Create Stripe account at https://stripe.com
2. Get test API keys from Dashboard → Developers → API keys
3. Add to `.env.local`:
   ```bash
   STRIPE_SECRET_KEY=sk_test_...
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRICE_ID_PRO=price_...
   STRIPE_CHECKOUT_SUCCESS_URL=http://localhost:3000/dashboard/billing/success
   STRIPE_CHECKOUT_CANCEL_URL=http://localhost:3000/dashboard/billing/cancel
   STRIPE_CUSTOMER_PORTAL_RETURN_URL=http://localhost:3000/dashboard/billing
   ```

**Reference:** https://docs.stripe.com/keys

#### Step 2: Create Products in Stripe Dashboard

1. Navigate to Dashboard → Product catalog (test mode)
2. Create products and pricing plans
3. Copy Price IDs to environment variables

**Reference:** https://docs.stripe.com/payments/checkout/build-subscriptions

#### Step 3: Database Schema Updates

Create migration to add billing columns to profiles:

```sql
-- supabase/migrations/[timestamp]_add_stripe_to_profiles.sql
alter table public.profiles
add column if not exists plan text default 'free' check (plan in ('free', 'pro', 'team')),
add column if not exists stripe_customer_id text unique,
add column if not exists stripe_subscription_id text,
add column if not exists stripe_subscription_status text;

create index if not exists idx_profiles_stripe_customer_id 
on public.profiles(stripe_customer_id);
```

#### Step 4: Install Stripe SDK

```bash
npm install stripe @stripe/stripe-js
```

#### Step 5: Create API Routes

**`app/api/billing/create-checkout-session/route.ts`:**
- Authenticates user
- Creates or retrieves Stripe customer
- Creates Checkout Session
- Returns URL for redirect

**`app/api/stripe/webhook/route.ts`:**
- Verifies webhook signature
- Handles subscription events:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
- Updates user plan in database

**`app/api/billing/customer-portal/route.ts`:**
- Creates Customer Portal session
- Returns URL for redirect

**See complete code examples in:** `.clinefiles/stripe/stripe-integration.md`

#### Step 6: Configure Webhooks

1. Dashboard → Developers → Webhooks (test mode)
2. Add endpoint: `http://localhost:3000/api/stripe/webhook`
3. Select events to listen for
4. Copy signing secret to `.env.local`

**For local testing:**
```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

**Reference:** https://docs.stripe.com/webhooks

#### Step 7: Frontend Components

Create billing page at `app/dashboard/billing/page.tsx`:
- Display current plan
- Show available plans with pricing
- Subscribe buttons for upgrades
- Manage Billing button (Customer Portal link)

**Components needed:**
- `components/subscribe-button.tsx` - Initiates Checkout
- `components/manage-billing-button.tsx` - Opens Customer Portal

**See complete component code in:** `.clinefiles/stripe/stripe-integration.md`

#### Step 8: Feature Gating

Implement plan-based access control:

```typescript
// lib/subscription.ts
export async function requirePlan(plan: 'pro' | 'team') {
  const userPlan = await getUserPlan();
  const planHierarchy = { free: 0, pro: 1, team: 2 };
  return planHierarchy[userPlan] >= planHierarchy[plan];
}
```

Use in API routes and components to restrict features.

#### Step 9: Testing

**Test cards:** https://docs.stripe.com/testing
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
```

**Test checklist:**
- [ ] User can create checkout session
- [ ] Checkout redirects to Stripe
- [ ] Successful payment creates subscription
- [ ] Webhook updates user plan
- [ ] Customer Portal opens correctly
- [ ] Feature gating works

### Production Deployment

1. Switch to live API keys in production
2. Create live products and prices
3. Configure live webhook endpoint
4. Update environment variables
5. Test end-to-end with real payment

**Reference:** `.clinefiles/stripe/stripe-integration.md` (Section 12)

---

## Phase 6 Completion Checklist

**ReactFlow (if applicable):**
- [ ] ReactFlow installed
- [ ] Basic flow editor implemented
- [ ] Custom node types created (if needed)
- [ ] Save/load functionality working
- [ ] Flow persists to database

**Real-time (if applicable):**
- [ ] Realtime subscriptions set up
- [ ] Updates reflect immediately
- [ ] Cleanup on unmount

**File Uploads (if applicable):**
- [ ] Storage bucket created
- [ ] Upload functionality working
- [ ] Files accessible

**Analytics (if applicable):**
- [ ] Charts components installed
- [ ] Data visualization working

**Stripe Billing (if applicable):**
- [ ] Stripe account created and test keys obtained
- [ ] Products and prices created in Stripe Dashboard
- [ ] Environment variables configured (test mode)
- [ ] Database migration added stripe columns to profiles
- [ ] Stripe SDK installed (stripe, @stripe/stripe-js)
- [ ] Checkout Session API route created and working
- [ ] Webhook handler created and signature verification working
- [ ] Webhook endpoint configured in Stripe Dashboard
- [ ] Customer Portal API route created
- [ ] Billing page created with plan display
- [ ] Subscribe buttons redirect to Stripe Checkout
- [ ] Manage Billing button opens Customer Portal
- [ ] Feature gating implemented (requirePlan function)
- [ ] Test payment flow completed successfully
- [ ] Webhook updates user plan in database
- [ ] Plan display updates after subscription change

---

## Next Phase

**Proceed to:** [Phase 7: Polish & Documentation](./phase-7-polish-and-docs.md)
