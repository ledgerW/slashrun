import { redirect } from 'next/navigation';
import type { ReactNode } from 'react';
import { getUserSession } from '@/lib/auth';
import { AuthProvider } from './_providers/AuthProvider';
import { UIStateProvider } from './_providers/UIStateProvider';
import { WorkspaceShell } from './_components/WorkspaceShell';

export default async function WorkspaceLayout({ children }: { children: ReactNode }) {
  const user = await getUserSession();

  if (!user) {
    redirect('/login');
  }

  return (
    <AuthProvider initialUser={user}>
      <UIStateProvider>
        <WorkspaceShell>{children}</WorkspaceShell>
      </UIStateProvider>
    </AuthProvider>
  );
}
