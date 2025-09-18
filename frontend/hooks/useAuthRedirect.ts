'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/providers/AuthProvider';

interface AuthRedirectOptions {
  when: 'authenticated' | 'unauthenticated';
  redirectTo: string;
  replace?: boolean;
}

export function useAuthRedirect({ when, redirectTo, replace = true }: AuthRedirectOptions) {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (when === 'unauthenticated' && !user) {
      if (replace) {
        router.replace(redirectTo);
      } else {
        router.push(redirectTo);
      }
    }

    if (when === 'authenticated' && user) {
      if (replace) {
        router.replace(redirectTo);
      } else {
        router.push(redirectTo);
      }
    }
  }, [user, when, redirectTo, replace, router]);
}
