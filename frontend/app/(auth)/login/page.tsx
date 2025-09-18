import { redirect } from 'next/navigation';
import { getUserSession } from '@/lib/auth';
import styles from '../auth-layout.module.css';
import { LoginForm } from './LoginForm';

export default async function LoginPage() {
  const existingUser = await getUserSession();
  if (existingUser) {
    redirect('/');
  }

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
      <LoginForm />
    </article>
  );
}
