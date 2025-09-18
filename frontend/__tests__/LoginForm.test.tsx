import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('@/lib/server-actions', () => ({
  loginAction: vi.fn(),
}));

import { LoginForm } from '@/app/(auth)/login/LoginForm';
import { ToastProvider } from '@/providers/ToastProvider';
import { loginAction } from '@/lib/server-actions';

function renderLoginForm() {
  return render(
    <ToastProvider>
      <LoginForm />
    </ToastProvider>,
  );
}

const loginActionMock = vi.mocked(loginAction);

describe('LoginForm', () => {
  beforeEach(() => {
    loginActionMock.mockReset();
  });

  it('validates required fields before submitting', async () => {
    renderLoginForm();

    await userEvent.click(screen.getByRole('button', { name: /enter workspace/i }));

    expect(loginActionMock).not.toHaveBeenCalled();
    expect(await screen.findByText('Enter your email address.')).toBeInTheDocument();
    expect(screen.getByText('Enter your password.')).toBeInTheDocument();
  });

  it('submits form values to loginAction when valid', async () => {
    loginActionMock.mockResolvedValue(undefined);
    renderLoginForm();

    await userEvent.type(screen.getByLabelText(/email address/i), 'agent@slash.run');
    await userEvent.type(screen.getByLabelText(/password/i), 'topsecret');

    await userEvent.click(screen.getByRole('button', { name: /enter workspace/i }));

    await waitFor(() => {
      expect(loginActionMock).toHaveBeenCalledWith({
        email: 'agent@slash.run',
        password: 'topsecret',
      });
    });
  });

  it('shows server error feedback when loginAction fails', async () => {
    loginActionMock.mockResolvedValue({ success: false, message: 'Invalid credentials' });
    renderLoginForm();

    await userEvent.type(screen.getByLabelText(/email address/i), 'agent@slash.run');
    await userEvent.type(screen.getByLabelText(/password/i), 'wrongpass');

    await userEvent.click(screen.getByRole('button', { name: /enter workspace/i }));

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Unable to sign in');
    expect(alert).toHaveTextContent('Invalid credentials');
    await waitFor(() => {
      expect(alert).toHaveFocus();
    });

    expect(await screen.findByText('Authentication failed')).toBeInTheDocument();
  });
});
