'use client';

import { useRouter } from 'next/navigation';
import { useState, type CSSProperties, type FormEvent } from 'react';
import styles from '../auth-layout.module.css';

interface LoginResponse {
  success: boolean;
  message?: string;
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrors(null);

    if (!email || !password) {
      setErrors('Enter both email and password to continue.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = (await response.json()) as LoginResponse;

      if (!response.ok || !data.success) {
        throw new Error(data.message ?? 'Unable to authenticate.');
      }

      router.push('/');
    } catch (error) {
      setErrors(error instanceof Error ? error.message : 'Unexpected error occurred.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <article className={styles.authCard} aria-labelledby="login-title">
      <header className={styles.authHeader}>
        <span className="label">SlashRun Control</span>
        <h1 id="login-title" className={styles.authHeaderTitle}>
          Access Workspace
        </h1>
        <p className={styles.authHeaderSubtitle}>
          Authenticate with your operations account to continue the simulation briefing.
        </p>
      </header>
      <form onSubmit={handleSubmit} noValidate>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <label htmlFor="email" className="label">
            Email Address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            aria-required="true"
            style={inputStyle}
          />
          <label htmlFor="password" className="label">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            aria-required="true"
            style={inputStyle}
          />
          {errors ? (
            <p role="alert" style={errorStyle}>
              {errors}
            </p>
          ) : null}
          <button
            type="submit"
            className="label"
            disabled={isSubmitting}
            style={{
              ...buttonStyle,
              opacity: isSubmitting ? 0.75 : 1,
              cursor: isSubmitting ? 'wait' : 'pointer',
            }}
          >
            {isSubmitting ? 'Verifying…' : 'Enter Workspace'}
          </button>
        </div>
      </form>
    </article>
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

const errorStyle: CSSProperties = {
  padding: '12px 14px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid rgba(255, 92, 92, 0.45)',
  background: 'rgba(255, 92, 92, 0.14)',
  color: 'var(--color-danger)',
};
