'use client';

import type { ReactNode } from 'react';
import layoutStyles from '@/styles/layout.module.css';
import { cn } from '@/lib/utils';

interface PanelProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export function Panel({ title, subtitle, children, actions, className }: PanelProps) {
  return (
    <section className={cn(layoutStyles.panel, className)} aria-label={title}>
      <header
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 'var(--space-3)',
        }}
      >
        <div>
          {title ? (
            <h2
              style={{
                margin: 0,
                color: 'var(--color-text-primary)',
                fontSize: '18px',
                letterSpacing: '0.04em',
              }}
            >
              {title}
            </h2>
          ) : null}
          {subtitle ? (
            <p
              style={{
                marginTop: '4px',
                color: 'var(--color-text-muted)',
                fontSize: '13px',
              }}
            >
              {subtitle}
            </p>
          ) : null}
        </div>
        {actions ? <div>{actions}</div> : null}
      </header>
      <div>{children}</div>
    </section>
  );
}
