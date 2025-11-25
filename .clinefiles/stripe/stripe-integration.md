# Stripe Integration Guide

**Purpose:** Complete guide for integrating Stripe payments into Next.js applications

**Use this guide when:**
- Adding subscription billing to your application
- Implementing one-time payments
- Managing customer billing portals
- Handling webhook events for payment lifecycle

---

## Overview

This guide covers Stripe integration for Next.js + Supabase applications using:
- **Stripe Checkout** - Pre-built payment pages
- **Stripe Billing** - Subscription management
- **Customer Portal** - Self-service billing management
- **Webhooks** - Payment event handling

**Official Stripe Documentation:**
- Stripe Overview: https://docs.stripe.com/get-started
- Checkout Quickstart: https://docs.stripe.com/checkout/quickstart
- Subscriptions Guide: https://docs.stripe.com/billing/subscriptions/overview
- Webhooks Guide: https://docs.stripe.com/webhooks
- Customer Portal: https://docs.stripe.com/customer-management/integrate-customer-portal

---

## 1. Stripe Account Setup

### 1.1 Create Stripe Account

1. Sign up at https://stripe.com (free account)
2. Complete account verification
3. Navigate to Dashboard → Developers → API keys

**Reference:** https://docs.stripe.com/get-started

### 1.2 Test Mode vs Production

**Always use test mode for development:**
- Test keys start with `sk_test_...` and `pk_test_...`
- Test mode has separate products, prices, and customers
- No real charges occur in test mode

**Production mode:**
- Live keys start with `sk_live_...` and `pk_live_...`
- Switch to production only when ready to accept real payments
- Requires business verification

**Reference:** https://docs.stripe.com/keys

### 1.3 Required API Keys

Navigate to **Dashboard → Developers → API keys** (ensure test mode is active):

```bash
# Publishable key (client-side, safe to expose)
pk_test_51...

# Secret key (server-side only, NEVER expose)
sk_test_51...
```

**Reference:** https://docs.stripe.com/keys

---

## 2. Environment Variables Setup

### 2.1 Add to `.env.local`

```bash
# Stripe API Keys (Test Mode)
STRIPE_SECRET_KEY=sk_test_51...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51...

# Stripe Webhook Secret (from webhook endpoint configuration)
STRIPE_WEBHOOK_SECRET=whsec_...

# Stripe Product/Price IDs
STRIPE_PRICE_ID_PRO=price_...     # Monthly Pro plan
STRIPE_PRICE_ID_TEAM=price_...    # Monthly Team plan (optional)

# Checkout URLs (adjust to your routes)
STRIPE_CHECKOUT_SUCCESS_URL=http://localhost:3000/dashboard/billing/success
STRIPE_CHECKOUT_CANCEL_URL=http://localhost:3000/dashboard/billing/cancel

# Customer Portal URL
STRIPE_CUSTOMER_PORTAL_RETURN_URL=http://localhost:3000/dashboard/billing
```

**⚠️ Important:**
- Use `NEXT_PUBLIC_` prefix ONLY for publishable key
- Never expose secret key or webhook secret
- Update URLs when deploying to production

**Reference:** https://docs.stripe.com/testing-use-cases

---

## 3. Create Products and Prices

### 3.1 Dashboard Setup (Manual Step)

**Navigate to: Dashboard → Product catalog (test mode)**

1. Click "Add product"
2. Configure product:
   - **Name:** "Pro Plan" (or your plan name)
   - **Description:** Brief description of features
   - **Pricing model:** Standard pricing
   - **Price:** $29 (or your price)
   - **Billing period:** Monthly (or your preference)
   - **Recurring:** Yes

3. Save and copy the **Price ID** (starts with `price_...`)
4. Add Price ID to `.env.local` as `STRIPE_PRICE_ID_PRO`

**Create additional plans as needed** (Team, Enterprise, etc.)

**Reference:** https://docs.stripe.com/payments/checkout/build-subscriptions

---

## 4. Database Schema Updates

### 4.1 Add Columns to Profiles Table

**Create migration:** `supabase/migrations/[timestamp]_add_stripe_to_profiles.sql`

```sql
-- Add Stripe-related columns to profiles table
alter table public.profiles
add column if not exists plan text default 'free' check (plan in ('free', 'pro', 'team')),
add column if not exists stripe_customer_id text unique,
add column if not exists stripe_subscription_id text,
add column if not exists stripe_subscription_status text;

-- Add index for faster lookups
create index if not exists idx_profiles_stripe_customer_id 
on public.profiles(stripe_customer_id);

-- Update RLS policies to allow users to read their own plan
-- (existing policies should already cover this, but verify)
```

**Adjust plan enum values** to match your product names.

**Reference:** `.clinefiles/supabase/database/create_migrations.md`

---

## 5. Install Stripe SDK

```bash
npm install stripe @stripe/stripe-js
```

**Packages:**
- `stripe` - Server-side SDK for API calls
- `@stripe/stripe-js` - Client-side SDK (optional, only if using Stripe Elements)

---

## 6. Create Checkout Session API Route

### 6.1 Checkout Session Endpoint

**`app/api/billing/create-checkout-session/route.ts`:**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
});

export async function POST(request: NextRequest) {
  try {
    // 1. Authenticate user
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // 2. Get or create Stripe customer
    const { data: profile } = await supabase
      .from('profiles')
      .select('stripe_customer_id, email')
      .eq('id', user.id)
      .single();

    let customerId = profile?.stripe_customer_id;

    // Create customer if doesn't exist
    if (!customerId) {
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: {
          supabase_user_id: user.id,
        },
      });
      
      customerId = customer.id;
      
      // Save customer ID to database
      await supabase
        .from('profiles')
        .update({ stripe_customer_id: customerId })
        .eq('id', user.id);
    }

    // 3. Get price ID from request body (or use default)
    const body = await request.json();
    const priceId = body.priceId || process.env.STRIPE_PRICE_ID_PRO;

    // 4. Create Checkout Session
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      customer: customerId,
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: process.env.STRIPE_CHECKOUT_SUCCESS_URL!,
      cancel_url: process.env.STRIPE_CHECKOUT_CANCEL_URL!,
      metadata: {
        user_id: user.id,
      },
    });

    // 5. Return session URL
    return NextResponse.json({ url: session.url });
    
  } catch (error) {
    console.error('Checkout error:', error);
    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}
```

**Key Points:**
- Requires authenticated user (via Supabase)
- Creates or retrieves Stripe customer
- Links Stripe customer to Supabase user
- Returns Checkout URL for redirect

**Reference:** https://docs.stripe.com/api/checkout/sessions

---

## 7. Create Webhook Handler

### 7.1 Webhook Endpoint Configuration

**⚠️ CRITICAL: Raw Body Required**

Stripe webhooks require the **raw request body** for signature verification. Next.js needs special configuration.

**`app/api/stripe/webhook/route.ts`:**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
});

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(request: NextRequest) {
  try {
    // 1. Get raw body and signature
    const body = await request.text();
    const signature = request.headers.get('stripe-signature');

    if (!signature) {
      return NextResponse.json(
        { error: 'Missing signature' },
        { status: 400 }
      );
    }

    // 2. Verify webhook signature
    let event: Stripe.Event;
    try {
      event = stripe.webhooks.constructEvent(
        body,
        signature,
        webhookSecret
      );
    } catch (err) {
      console.error('Webhook signature verification failed:', err);
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 400 }
      );
    }

    // 3. Handle different event types
    const supabase = await createClient();
    
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;
        const userId = session.metadata?.user_id;
        
        if (userId && session.customer) {
          await supabase
            .from('profiles')
            .update({
              stripe_customer_id: session.customer as string,
              stripe_subscription_id: session.subscription as string,
            })
            .eq('id', userId);
        }
        break;
      }

      case 'customer.subscription.created':
      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription;
        
        // Determine plan from price ID
        const priceId = subscription.items.data[0]?.price.id;
        let plan = 'free';
        
        if (priceId === process.env.STRIPE_PRICE_ID_PRO) {
          plan = 'pro';
        } else if (priceId === process.env.STRIPE_PRICE_ID_TEAM) {
          plan = 'team';
        }
        
        await supabase
          .from('profiles')
          .update({
            plan,
            stripe_subscription_id: subscription.id,
            stripe_subscription_status: subscription.status,
          })
          .eq('stripe_customer_id', subscription.customer as string);
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription;
        
        await supabase
          .from('profiles')
          .update({
            plan: 'free',
            stripe_subscription_id: null,
            stripe_subscription_status: 'canceled',
          })
          .eq('stripe_customer_id', subscription.customer as string);
        break;
      }

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
    
  } catch (error) {
    console.error('Webhook error:', error);
    return NextResponse.json(
      { error: 'Webhook handler failed' },
      { status: 500 }
    );
  }
}
```

**Key Events to Handle:**
- `checkout.session.completed` - Link customer after checkout
- `customer.subscription.created` - New subscription started
- `customer.subscription.updated` - Plan changed or renewed
- `customer.subscription.deleted` - Subscription canceled

**Reference:** https://docs.stripe.com/webhooks

### 7.2 Configure Webhook in Stripe Dashboard

1. Go to **Dashboard → Developers → Webhooks** (test mode)
2. Click "Add endpoint"
3. Enter endpoint URL: `http://localhost:3000/api/stripe/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Save and copy the **Signing secret** (starts with `whsec_...`)
6. Add signing secret to `.env.local` as `STRIPE_WEBHOOK_SECRET`

**For local testing:**
- Use Stripe CLI: `stripe listen --forward-to localhost:3000/api/stripe/webhook`
- Or use ngrok for public URL

**Reference:** https://docs.stripe.com/webhooks

---

## 8. Customer Portal Integration

### 8.1 Enable Customer Portal

**Dashboard Setup (Manual Step):**

1. Go to **Dashboard → Settings → Billing → Customer portal** (test mode)
2. Click "Activate test link" (or configure settings)
3. Configure portal settings:
   - Allow customers to update payment methods
   - Allow customers to cancel subscriptions
   - Set default return URL
4. Save configuration

**Reference:** https://docs.stripe.com/no-code/customer-portal

### 8.2 Portal Session API Route

**`app/api/billing/customer-portal/route.ts`:**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
});

export async function POST(request: NextRequest) {
  try {
    // 1. Authenticate user
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // 2. Get Stripe customer ID
    const { data: profile } = await supabase
      .from('profiles')
      .select('stripe_customer_id')
      .eq('id', user.id)
      .single();

    if (!profile?.stripe_customer_id) {
      return NextResponse.json(
        { error: 'No billing account found' },
        { status: 404 }
      );
    }

    // 3. Create portal session
    const session = await stripe.billingPortal.sessions.create({
      customer: profile.stripe_customer_id,
      return_url: process.env.STRIPE_CUSTOMER_PORTAL_RETURN_URL!,
    });

    // 4. Return portal URL
    return NextResponse.json({ url: session.url });
    
  } catch (error) {
    console.error('Portal error:', error);
    return NextResponse.json(
      { error: 'Failed to create portal session' },
      { status: 500 }
    );
  }
}
```

**Reference:** https://docs.stripe.com/api/customer_portal/sessions/create

---

## 9. Frontend Components

### 9.1 Billing Page

**`app/dashboard/billing/page.tsx`:**

```typescript
import { createClient } from '@/lib/supabase/server';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { SubscribeButton } from '@/components/subscribe-button';
import { ManageBillingButton } from '@/components/manage-billing-button';
import { CheckCircle } from 'lucide-react';

export default async function BillingPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  const { data: profile } = await supabase
    .from('profiles')
    .select('plan, stripe_subscription_status')
    .eq('id', user?.id)
    .single();

  const plan = profile?.plan || 'free';
  const isActive = profile?.stripe_subscription_status === 'active';

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Billing</h1>
        <p className="text-muted-foreground">
          Manage your subscription and billing information
        </p>
      </div>

      {/* Current Plan */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle>Current Plan</CardTitle>
              <CardDescription>
                You are on the{' '}
                <span className="font-semibold capitalize">{plan}</span> plan
              </CardDescription>
            </div>
            {isActive && (
              <Badge variant="success">Active</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {plan !== 'free' && isActive && (
            <ManageBillingButton />
          )}
        </CardContent>
      </Card>

      {/* Available Plans */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Free Plan</CardTitle>
            <CardDescription>Basic features</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-3xl font-bold">$0/mo</div>
            <ul className="space-y-2">
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Feature 1</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Feature 2</span>
              </li>
            </ul>
            {plan === 'free' && (
              <Badge variant="outline">Current Plan</Badge>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pro Plan</CardTitle>
            <CardDescription>Advanced features</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-3xl font-bold">$29/mo</div>
            <ul className="space-y-2">
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Everything in Free</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Premium Feature 1</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Premium Feature 2</span>
              </li>
            </ul>
            {plan === 'pro' ? (
              <Badge variant="outline">Current Plan</Badge>
            ) : (
              <SubscribeButton priceId={process.env.STRIPE_PRICE_ID_PRO!} />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### 9.2 Subscribe Button Component

**`components/subscribe-button.tsx`:**

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

export function SubscribeButton({ priceId }: { priceId: string }) {
  const [loading, setLoading] = useState(false);

  async function handleSubscribe() {
    setLoading(true);
    try {
      const response = await fetch('/api/billing/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId }),
      });

      const { url, error } = await response.json();
      
      if (error) throw new Error(error);
      if (url) window.location.href = url;
      
    } catch (error) {
      toast.error('Failed to start checkout');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Button onClick={handleSubscribe} disabled={loading} className="w-full">
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      Subscribe
    </Button>
  );
}
```

### 9.3 Manage Billing Button

**`components/manage-billing-button.tsx`:**

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

export function ManageBillingButton() {
  const [loading, setLoading] = useState(false);

  async function handleManage() {
    setLoading(true);
    try {
      const response = await fetch('/api/billing/customer-portal', {
        method: 'POST',
      });

      const { url, error } = await response.json();
      
      if (error) throw new Error(error);
      if (url) window.location.href = url;
      
    } catch (error) {
      toast.error('Failed to open billing portal');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Button onClick={handleManage} disabled={loading} variant="outline">
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      Manage Billing
    </Button>
  );
}
```

---

## 10. Feature Gating Based on Plan

### 10.1 Server-Side Feature Check

**`lib/subscription.ts`:**

```typescript
import { createClient } from '@/lib/supabase/server';

export async function getUserPlan() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) return 'free';
  
  const { data: profile } = await supabase
    .from('profiles')
    .select('plan')
    .eq('id', user.id)
    .single();
  
  return profile?.plan || 'free';
}

export async function requirePlan(plan: 'pro' | 'team') {
  const userPlan = await getUserPlan();
  
  const planHierarchy = { free: 0, pro: 1, team: 2 };
  const required = planHierarchy[plan];
  const current = planHierarchy[userPlan as keyof typeof planHierarchy] || 0;
  
  return current >= required;
}
```

### 10.2 Usage in API Routes

```typescript
import { requirePlan } from '@/lib/subscription';
import { NextResponse } from 'next/server';

export async function POST() {
  // Check if user has required plan
  const hasAccess = await requirePlan('pro');
  
  if (!hasAccess) {
    return NextResponse.json(
      { error: 'This feature requires a Pro plan' },
      { status: 403 }
    );
  }
  
  // Proceed with protected functionality
  // ...
}
```

### 10.3 Client-Side Feature Check

**`components/pro-feature.tsx`:**

```typescript
import { requirePlan } from '@/lib/subscription';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export async function ProFeature({ children }: { children: React.ReactNode }) {
  const hasAccess = await requirePlan('pro');
  
  if (!hasAccess) {
    return (
      <div className="p-6 border rounded-lg text-center space-y-4">
        <p className="text-muted-foreground">
          This feature requires a Pro plan
        </p>
        <Button asChild>
          <Link href="/dashboard/billing">Upgrade to Pro</Link>
        </Button>
      </div>
    );
  }
  
  return <>{children}</>;
}
```

---

## 11. Testing

### 11.1 Test Credit Cards

Stripe provides test cards for various scenarios:

**Successful Payment:**
```
Card: 4242 4242 4242 4242
Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

**Declined Card:**
```
Card: 4000 0000 0000 0002
```

**Requires Authentication (3D Secure):**
```
Card: 4000 0027 6000 3184
```

**Reference:** https://docs.stripe.com/testing

### 11.2 Testing Webhooks Locally

**Option 1: Stripe CLI**
```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
stripe trigger checkout.session.completed
```

**Option 2: Use test mode webhook**
- Create test webhook endpoint in Stripe Dashboard
- Use ngrok or similar for public URL

### 11.3 Testing Checklist

- [ ] User can create checkout session
- [ ] Checkout redirects to Stripe
- [ ] Successful payment creates subscription
- [ ] Webhook updates user plan in database
- [ ] User sees updated plan in billing page
- [ ] Customer Portal opens correctly
- [ ] User can manage subscription in portal
- [ ] Cancellation updates plan to free
- [ ] Feature gating works correctly

---

## 12. Production Deployment

### 12.1 Switch to Live Mode

1. Get live API keys from **Dashboard → Developers → API keys** (live mode)
2. Update environment variables in production:
   ```bash
   STRIPE_SECRET_KEY=sk_live_...
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
   ```
3. Create live products and prices
4. Update price IDs in environment variables
5. Configure live webhook endpoint
6. Update webhook secret
7. Test end-to-end with real payment method

### 12.2 Production Webhook Setup

1. Go to **Dashboard → Developers → Webhooks** (live mode)
2. Add endpoint with your production URL:
   ```
   https://yourdomain.com/api/stripe/webhook
   ```
3. Select same events as test mode
4. Save signing secret to production environment

### 12.3 Update Success/Cancel URLs

```bash
STRIPE_CHECKOUT_SUCCESS_URL=https://yourdomain.com/dashboard/billing/success
STRIPE_CHECKOUT_CANCEL_URL=https://yourdomain.com/dashboard/billing/cancel
STRIPE_CUSTOMER_PORTAL_RETURN_URL=https://yourdomain.com/dashboard/billing
```

---

## 13. Common Issues & Troubleshooting

### Issue: "No signatures found matching the expected signature"

**Cause:** Webhook signature verification failed

**Solution:**
- Verify `STRIPE_WEBHOOK_SECRET` is correct
- Ensure using raw body (not parsed JSON)
- Check webhook endpoint is receiving POST requests
- Verify signing secret is from correct mode (test/live)

### Issue: "Customer not found"

**Cause:** Customer ID doesn't exist in Stripe

**Solution:**
- Verify customer was created in correct mode (test/live)
- Check `stripe_customer_id` in database matches Stripe
- Ensure customer creation error handling is correct

### Issue: "Checkout session expires immediately"

**Cause:** Success/cancel URLs are invalid

**Solution:**
- Verify URLs are absolute (include protocol)
- Check URLs are accessible
- Test URLs in browser

### Issue: "Plan not updating after payment"

**Cause:** Webhook not firing or handling incorrectly

**Solution:**
- Check webhook endpoint is publicly accessible
- Verify webhook events are configured
- Check webhook logs in Stripe Dashboard
- Test webhook with Stripe CLI

### Issue: "Customer Portal not loading"

**Cause:** Portal not configured or customer has no subscriptions

**Solution:**
- Activate Customer Portal in Dashboard
- Verify customer has active subscription
- Check customer ID is correct

---

## 14. Security Best Practices

### 14.1 Environment Variables

- ✅ Never commit secret keys to version control
- ✅ Use different keys for dev/staging/production
- ✅ Rotate keys regularly
- ✅ Use environment-specific `.env` files

### 14.2 Webhook Verification

- ✅ Always verify webhook signatures
- ✅ Use raw body for signature verification
- ✅ Handle webhook failures gracefully
- ✅ Log webhook events for debugging

### 14.3 Customer Data

- ✅ Never store card details yourself (use Stripe)
- ✅ Use Stripe Customer Portal for card updates
- ✅ Implement proper error handling
- ✅ Follow PCI compliance guidelines

### 14.4 API Routes

- ✅ Require authentication for all billing routes
- ✅ Validate user owns the subscription
- ✅ Rate limit API endpoints
- ✅ Log all billing operations

---

## 15. Additional Resources

**Official Stripe Documentation:**
- Getting Started: https://docs.stripe.com/get-started
- API Reference: https://docs.stripe.com/api
- Checkout Guide: https://docs.stripe.com/checkout/quickstart
- Subscriptions: https://docs.stripe.com/billing/subscriptions/overview
- Webhooks: https://docs.stripe.com/webhooks
- Customer Portal: https://docs.stripe.com/customer-management/integrate-customer-portal
- Testing: https://docs.stripe.com/testing

**Integration Examples:**
- Next.js + Stripe: https://github.com/vercel/nextjs-subscription-payments
- Vercel Guide: https://vercel.com/guides/getting-started-with-nextjs-typescript-stripe

**Stripe Dashboard:**
- Test Mode: https://dashboard.stripe.com/test
- Live Mode: https://dashboard.stripe.com/live

**Support:**
- Stripe Support: https://support.stripe.com
- Community Forum: https://support.stripe.com/questions
