import React from 'react';
import { render, screen } from '@testing-library/react';
import { WorkspaceShell } from '@/app/(workspace)/_components/WorkspaceShell';
import { AuthProvider } from '@/app/(workspace)/_providers/AuthProvider';
import { UIStateProvider } from '@/app/(workspace)/_providers/UIStateProvider';
import type { AuthenticatedUser } from '@/lib/types';

function renderWorkspace(children: React.ReactNode) {
  const user: AuthenticatedUser = {
    userId: 'analyst-1',
    email: 'analyst@slash.run',
    token: 'test-token',
  };

  return render(
    <AuthProvider initialUser={user}>
      <UIStateProvider>
        <WorkspaceShell>{children}</WorkspaceShell>
      </UIStateProvider>
    </AuthProvider>,
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
