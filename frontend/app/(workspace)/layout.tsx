import { Suspense } from 'react';
import { redirect } from 'next/navigation';
import type { ReactNode } from 'react';
import { getUserSession } from '@/lib/auth';
import { AuthProvider } from '@/providers/AuthProvider';
import { UIStateProvider } from './_providers/UIStateProvider';
import { QueryProvider } from '@/providers/QueryProvider';
import { SimulationProvider } from '@/providers/SimulationProvider';
import { WorkspaceLoadingState } from './_components/LoadingStates';

export default async function WorkspaceLayout({ children }: { children: ReactNode }) {
  const user = await getUserSession();

  if (!user) {
    redirect('/login');
  }

  return (
    <AuthProvider initialUser={user}>
      <QueryProvider>
        <UIStateProvider>
          <SimulationProvider>
            <Suspense fallback={<WorkspaceLoadingState />}>{children}</Suspense>
          </SimulationProvider>
        </UIStateProvider>
      </QueryProvider>
    </AuthProvider>
  );
}
