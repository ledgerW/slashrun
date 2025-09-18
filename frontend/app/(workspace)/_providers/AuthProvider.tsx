'use client';

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useRouter } from 'next/navigation';
import type { AuthenticatedUser } from '@/lib/types';
import { logoutAction } from '@/lib/server-actions';
import { useToast } from './ToastProvider';

interface AuthContextValue {
  user: AuthenticatedUser | null;
  setUser: (user: AuthenticatedUser | null) => void;
  logout: () => Promise<void>;
  isLoggingOut: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({
  children,
  initialUser,
}: {
  children: ReactNode;
  initialUser: AuthenticatedUser | null;
}) {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(initialUser);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const { pushToast } = useToast();

  const logout = useCallback(async () => {
    setIsLoggingOut(true);
    try {
      await logoutAction();
      setUser(null);
      router.push('/login');
      router.refresh();
    } catch (error) {
      console.error('Failed to logout user', error);
      pushToast({
        title: 'Logout failed',
        description: 'Unable to terminate your session. Please try again.',
        variant: 'error',
      });
      throw error;
    } finally {
      setIsLoggingOut(false);
    }
  }, [router, pushToast]);

  const value = useMemo(
    () => ({ user, setUser, logout, isLoggingOut }),
    [user, logout, isLoggingOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
