'use client';

import layoutStyles from '@/styles/layout.module.css';
import { cn } from '@/lib/utils';

export function TimelineFooter({ className }: { className?: string }) {
  return (
    <footer
      className={cn(layoutStyles.timelineFooter, className)}
      aria-label="Timeline controls"
    >
      <div className={layoutStyles.timelineTickers}>
        <span className="label">Timestep</span>
        <span style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>
          24 / 64
        </span>
      </div>
      <div className={layoutStyles.timelineScale} role="presentation" />
      <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
        <button type="button" className={layoutStyles.controlButton}>
          Step Back
        </button>
        <button type="button" className={layoutStyles.controlButton}>
          Step Forward
        </button>
      </div>
    </footer>
  );
}
