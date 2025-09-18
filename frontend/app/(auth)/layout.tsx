import type { ReactNode } from 'react';
import styles from './auth-layout.module.css';

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className={styles.authShell}>
      <main role="main">{children}</main>
    </div>
  );
}
