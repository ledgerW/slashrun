'use client';

import layoutStyles from '@/styles/layout.module.css';
import { useAuth } from '@/providers/AuthProvider';
import { useUIState } from '../_providers/UIStateProvider';
import { ScenarioSwitcher } from './ScenarioSwitcher';

export function TopBar() {
  const { user, logout, isLoggingOut } = useAuth();
  const toggleTimeline = useUIState((state) => state.toggleTimeline);

  return (
    <header className={layoutStyles.topBar}>
      <div className={layoutStyles.brand}>
        <span className={layoutStyles.brandLogo} aria-hidden />
        <div>
          <span className="label">SlashRun</span>
          <p className={layoutStyles.brandName}>Gotham Desk</p>
        </div>
      </div>
      <div className={layoutStyles.controls}>
        <ScenarioSwitcher />
        <button
          type="button"
          onClick={toggleTimeline}
          className={layoutStyles.controlButton}
        >
          Toggle Timeline
        </button>
        <UserBadge email={user?.email ?? 'unassigned@slash.run'} name={user?.displayName} />
        <button
          type="button"
          className={layoutStyles.controlButton}
          onClick={() => {
            void logout();
          }}
          disabled={isLoggingOut}
        >
          {isLoggingOut ? 'Signing out…' : 'Logout'}
        </button>
      </div>
    </header>
  );
}

function UserBadge({ name, email }: { name?: string | null; email: string }) {
  const initials = (name ?? email)
    .split(' ')
    .map((part) => part.charAt(0))
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 12px',
        borderRadius: '999px',
        background: 'rgba(78, 160, 255, 0.16)',
        color: 'var(--color-text-primary)',
        fontSize: '13px',
      }}
      aria-label={`Signed in as ${name ?? email}`}
    >
      <span
        aria-hidden
        style={{
          width: '26px',
          height: '26px',
          borderRadius: '50%',
          background: 'rgba(78, 160, 255, 0.35)',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 600,
        }}
      >
        {initials || 'AN'}
      </span>
      <span>{name ?? email}</span>
    </span>
  );
}
