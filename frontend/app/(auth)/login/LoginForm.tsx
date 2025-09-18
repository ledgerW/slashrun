'use client';

import { useEffect, useRef, useState, useTransition, type CSSProperties } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { isRedirectError } from 'next/dist/client/components/redirect';
import {
  loginAction,
  type LoginActionFailure,
  type LoginActionResult,
} from '@/lib/server-actions';
import { useToast } from '@/providers/ToastProvider';

const loginSchema = z.object({
  email: z
    .string({ required_error: 'Enter your email address.' })
    .min(1, 'Enter your email address.')
    .email('Use a valid email address.'),
  password: z
    .string({ required_error: 'Enter your password.' })
    .min(1, 'Enter your password.'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

function isLoginFailure(result: LoginActionResult): result is LoginActionFailure {
  return Boolean(result) && typeof result === 'object' && 'success' in result && !result.success;
}

export function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setFocus,
    watch,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    mode: 'onSubmit',
    reValidateMode: 'onBlur',
    shouldFocusError: true,
  });
  const [serverError, setServerError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const errorSummaryRef = useRef<HTMLDivElement | null>(null);
  const { pushToast } = useToast();

  useEffect(() => {
    setFocus('email');
  }, [setFocus]);

  useEffect(() => {
    if (serverError) {
      errorSummaryRef.current?.focus();
    }
  }, [serverError]);

  useEffect(() => {
    const subscription = watch(() => {
      if (serverError) {
        setServerError(null);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [watch, serverError]);

  const handleLogin = (values: LoginFormValues) => {
    setServerError(null);
    startTransition(async () => {
      try {
        const result = await loginAction(values);
        if (isLoginFailure(result)) {
          const message = result.message || 'Unable to authenticate.';
          setServerError(message);
          pushToast({
            title: 'Authentication failed',
            description: message,
            variant: 'error',
          });
          setFocus('email');
        }
      } catch (error) {
        if (isRedirectError(error)) {
          throw error;
        }

        const message =
          error instanceof Error
            ? error.message
            : 'Unexpected authentication error';
        setServerError(message);
        pushToast({
          title: 'Authentication failed',
          description: message,
          variant: 'error',
        });
        setFocus('email');
      }
    });
  };

  const emailError = errors.email?.message;
  const passwordError = errors.password?.message;

  return (
    <form
      onSubmit={handleSubmit(handleLogin)}
      noValidate
      aria-describedby={serverError ? 'login-error' : undefined}
      style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}
    >
      {serverError ? (
        <div
          id="login-error"
          role="alert"
          aria-live="assertive"
          tabIndex={-1}
          ref={errorSummaryRef}
          style={serverErrorStyle}
        >
          <strong style={{ display: 'block', marginBottom: '6px' }}>Unable to sign in</strong>
          <span>{serverError}</span>
        </div>
      ) : null}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        <label htmlFor="email" className="label">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          aria-invalid={emailError ? 'true' : 'false'}
          aria-describedby={emailError ? 'email-error' : undefined}
          {...register('email')}
          style={inputStyle}
        />
        {emailError ? (
          <p id="email-error" role="alert" style={fieldErrorStyle}>
            {emailError}
          </p>
        ) : null}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        <label htmlFor="password" className="label">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          aria-invalid={passwordError ? 'true' : 'false'}
          aria-describedby={passwordError ? 'password-error' : undefined}
          {...register('password')}
          style={inputStyle}
        />
        {passwordError ? (
          <p id="password-error" role="alert" style={fieldErrorStyle}>
            {passwordError}
          </p>
        ) : null}
      </div>

      <button
        type="submit"
        className="label"
        disabled={isPending}
        aria-busy={isPending}
        style={{
          ...buttonStyle,
          opacity: isPending ? 0.75 : 1,
          cursor: isPending ? 'wait' : 'pointer',
        }}
      >
        {isPending ? 'Verifying…' : 'Enter Workspace'}
      </button>
    </form>
  );
}

const inputStyle: CSSProperties = {
  width: '100%',
  padding: '14px 16px',
  borderRadius: 'var(--radius-md)',
  border: '1px solid rgba(78, 160, 255, 0.2)',
  background: 'rgba(10, 14, 22, 0.95)',
  color: 'var(--color-text-primary)',
};

const buttonStyle: CSSProperties = {
  width: '100%',
  padding: '16px',
  borderRadius: 'var(--radius-md)',
  border: '1px solid rgba(78, 160, 255, 0.4)',
  background:
    'linear-gradient(135deg, rgba(78, 160, 255, 0.85) 0%, rgba(33, 57, 95, 0.92) 100%)',
  color: '#010409',
  fontWeight: 600,
  letterSpacing: '0.06em',
  textTransform: 'uppercase',
  transition: 'transform var(--transition-fast)',
};

const serverErrorStyle: CSSProperties = {
  padding: '12px 14px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid rgba(255, 92, 92, 0.45)',
  background: 'rgba(255, 92, 92, 0.14)',
  color: 'var(--color-danger)',
  outline: 'none',
};

const fieldErrorStyle: CSSProperties = {
  margin: 0,
  color: 'var(--color-danger)',
  fontSize: '13px',
};
