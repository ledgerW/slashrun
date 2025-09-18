'use client';

import type { CSSProperties } from 'react';
import layoutStyles from '@/styles/layout.module.css';
import { useAuth } from '../_providers/AuthProvider';
import { useUIState } from '../_providers/UIStateProvider';

const selectStyle: CSSProperties = {
  background: 'rgba(16, 24, 38, 0.85)',
  border: '1px solid rgba(78, 160, 255, 0.25)',
  borderRadius: 'var(--radius-md)',
  color: 'var(--color-text-primary)',
  padding: '12px 16px',
  minWidth: '220px',
};

const badgeStyle: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '8px',
  padding: '8px 12px',
  borderRadius: '999px',
  background: 'rgba(78, 160, 255, 0.16)',
  color: 'var(--color-text-primary)',
  fontSize: '13px',
};

export function TopBar() {
  const { user, logout } = useAuth();
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
        <div>
          <label
            htmlFor="scenario-select"
            className="label"
            style={{ display: 'block', marginBottom: '4px' }}
          >
            Scenario
          </label>
          <select
            id="scenario-select"
            name="scenario"
            defaultValue="baseline"
            style={selectStyle}
          >
            <option value="baseline">Baseline Sanctions</option>
            <option value="escalated">Escalated Conflict</option>
            <option value="energy">Energy Shock</option>
          </select>
        </div>
        <button
          type="button"
          onClick={toggleTimeline}
          className={layoutStyles.controlButton}
        >
          Toggle Timeline
        </button>
        <span style={badgeStyle}>
          <span className="label">Analyst</span>
          <span>{user?.email ?? 'unassigned@slash.run'}</span>
        </span>
        <button type="button" className={layoutStyles.controlButton} onClick={logout}>
          Logout
        </button>
      </div>
    </header>
  );
}
