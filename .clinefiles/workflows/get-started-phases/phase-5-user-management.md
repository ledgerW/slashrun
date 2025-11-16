# Phase 5: User Management [MANDATORY]

**Purpose:** Implement complete user management functionality

**Prerequisites:**
- Phase 4: CRUD operations complete

**References:**
- `.clinefiles/ui/supabase-blocks.md`
- `.clinefiles/supabase/auth-for-nextjs.md`

---

## Step 1: User Profile Page [MANDATORY]

**`app/dashboard/profile/page.tsx`:**
```typescript
import { createClient } from '@/lib/supabase/server';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import Link from 'next/link';

export default async function ProfilePage() {
  const supabase = await createClient();
  
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return <div>Not authenticated</div>;
  }

  const { data: profile } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', user.id)
    .single();

  return (
    <div className="max-w-2xl space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Profile</h1>
        <Button asChild>
          <Link href="/dashboard/profile/edit">Edit Profile</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>User Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src={profile?.avatar_url} />
              <AvatarFallback>
                {profile?.full_name?.[0] || user.email?.[0]}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold">{profile?.full_name || 'No name'}</p>
              <p className="text-sm text-muted-foreground">{user.email}</p>
            </div>
          </div>
          
          {profile?.bio && (
            <div>
              <p className="font-semibold">Bio</p>
              <p className="text-muted-foreground">{profile.bio}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## Step 2: Profile Edit Page [MANDATORY]

**`components/profile-form.tsx`:**
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
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  bio: z.string().optional(),
});

type ProfileFormValues = z.infer<typeof formSchema>;

export function ProfileForm({ profile }: { profile: any }) {
  const router = useRouter();
  const supabase = createClient();
  
  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      full_name: profile?.full_name || '',
      bio: profile?.bio || '',
    },
  });

  async function onSubmit(values: ProfileFormValues) {
    try {
      const { error } = await supabase
        .from('profiles')
        .update(values)
        .eq('id', profile.id);

      if (error) throw error;
      
      toast.success('Profile updated successfully');
      router.push('/dashboard/profile');
      router.refresh();
    } catch (error) {
      toast.error('Failed to update profile');
      console.error(error);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="full_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Full Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio</FormLabel>
              <FormControl>
                <Textarea {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <div className="flex gap-2">
          <Button type="submit">Save Changes</Button>
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

**`app/dashboard/profile/edit/page.tsx`:**
```typescript
import { createClient } from '@/lib/supabase/server';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProfileForm } from '@/components/profile-form';

export default async function EditProfilePage() {
  const supabase = await createClient();
  
  const { data: { user } } = await supabase.auth.getUser();
  
  const { data: profile } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', user?.id)
    .single();

  return (
    <div className="max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Edit Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <ProfileForm profile={profile} />
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## Step 3: Account Settings Page [MANDATORY]

**`app/dashboard/settings/page.tsx`:**
```typescript
import { createClient } from '@/lib/supabase/server';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PasswordChangeForm } from '@/components/password-change-form';
import { EmailChangeForm } from '@/components/email-change-form';

export default async function SettingsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold">Account Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
        </CardHeader>
        <CardContent>
          <PasswordChangeForm />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Change Email</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Current email: {user?.email}
          </p>
          <EmailChangeForm />
        </CardContent>
      </Card>
    </div>
  );
}
```

**`components/password-change-form.tsx`:**
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
import { createClient } from '@/lib/supabase/client';
import { toast } from 'sonner';

const formSchema = z.object({
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type PasswordFormValues = z.infer<typeof formSchema>;

export function PasswordChangeForm() {
  const supabase = createClient();
  
  const form = useForm<PasswordFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  });

  async function onSubmit(values: PasswordFormValues) {
    try {
      const { error } = await supabase.auth.updateUser({
        password: values.password
      });

      if (error) throw error;
      
      toast.success('Password updated successfully');
      form.reset();
    } catch (error) {
      toast.error('Failed to update password');
      console.error(error);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>New Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="confirmPassword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <Button type="submit">Update Password</Button>
      </form>
    </Form>
  );
}
```

---

## Step 4: Logout Button Implementation [MANDATORY]

**`components/logout-button.tsx`:**
```typescript
'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { createClient } from '@/lib/supabase/client';
import { LogOut } from 'lucide-react';
import { toast } from 'sonner';

export function LogoutButton() {
  const router = useRouter();
  const supabase = createClient();

  async function handleLogout() {
    try {
      const { error } = await supabase.auth.signOut();
      
      if (error) throw error;
      
      toast.success('Logged out successfully');
      router.push('/');
      router.refresh();
    } catch (error) {
      toast.error('Failed to log out');
      console.error(error);
    }
  }

  return (
    <Button 
      variant="ghost" 
      size="sm"
      onClick={handleLogout}
    >
      <LogOut className="mr-2 h-4 w-4" />
      Logout
    </Button>
  );
}
```

**Add to Sidebar Navigation (`components/nav-user.tsx` or `app-sidebar.tsx`):**
```typescript
import { LogoutButton } from '@/components/logout-button';

// In your sidebar footer or user menu
<LogoutButton />
```

---

## Step 5: Update Sidebar Navigation

Add user management links to navigation:

```typescript
const navItems = [
  { title: "Profile", url: "/dashboard/profile", icon: User },
  { title: "Settings", url: "/dashboard/settings", icon: Settings },
];
```

---

## Phase 5 Completion Checklist

- [ ] User profile view page implemented
- [ ] Profile edit functionality working
- [ ] Account settings page implemented
- [ ] Password change working
- [ ] Email change implemented (optional)
- [ ] Logout button added to navigation
- [ ] Logout functionality working
- [ ] Session properly cleared on logout
- [ ] Redirect to landing page after logout

**Verification:**
- [ ] Can view own profile
- [ ] Can edit profile information
- [ ] Can change password
- [ ] Logout button visible in navigation
- [ ] Logout works and clears session
- [ ] Redirects to home after logout

---

## Next Phase

**Proceed to:** [Phase 6: Advanced Features](./phase-6-advanced-features.md)
