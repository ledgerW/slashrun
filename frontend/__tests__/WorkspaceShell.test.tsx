import React from 'react';
import { render, screen } from '@testing-library/react';
import { WorkspaceShell } from '@/app/(workspace)/_components/WorkspaceShell';
import { AuthProvider } from '@/providers/AuthProvider';
import { UIStateProvider } from '@/app/(workspace)/_providers/UIStateProvider';
import { SimulationProvider } from '@/providers/SimulationProvider';
import { ToastProvider } from '@/providers/ToastProvider';
import type { AuthenticatedUser } from '@/lib/types';

vi.mock('@/hooks/useScenarioList', () => ({
  useScenarioList: () => ({ data: [], isLoading: false }),
}));

function renderWorkspace(children: React.ReactNode) {
  const user: AuthenticatedUser = {
    id: 'analyst-1',
    email: 'analyst@slash.run',
    displayName: 'Analyst One',
    roles: ['analyst'],
  };

  return render(
    <ToastProvider>
      <AuthProvider initialUser={user}>
        <UIStateProvider>
          <SimulationProvider>
            <WorkspaceShell>{children}</WorkspaceShell>
          </SimulationProvider>
        </UIStateProvider>
      </AuthProvider>
    </ToastProvider>,
  );
}

describe('WorkspaceShell', () => {
  it('renders skip link and core regions', () => {
    renderWorkspace(<p>Primary workspace content</p>);

    expect(screen.getByText('Skip to main content')).toHaveAttribute(
      'href',
      '#workspace-main',
    );
    expect(
      screen.getByRole('complementary', { name: /workspace primary navigation/i }),
    ).toBeInTheDocument();
    expect(screen.getAllByRole('banner').length).toBeGreaterThan(0);
    expect(screen.getByRole('main')).toHaveTextContent('Primary workspace content');
    expect(screen.getByLabelText('Evidence rail')).toBeInTheDocument();
    expect(screen.getByLabelText('Timeline controls')).toBeInTheDocument();
  });
});
