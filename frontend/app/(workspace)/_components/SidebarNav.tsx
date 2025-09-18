'use client';

import { useMemo } from 'react';
import layoutStyles from '@/styles/layout.module.css';
import { useUIState } from '../_providers/UIStateProvider';

interface NavItem {
  id: string;
  label: string;
  abbreviation: string;
  status?: 'active' | 'idle' | 'disabled';
}

const NAVIGATION_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Situation Overview', abbreviation: 'SO', status: 'active' },
  { id: 'timeline', label: 'Timeline', abbreviation: 'TL' },
  { id: 'map', label: 'Map Layers', abbreviation: 'ML' },
  { id: 'network', label: 'Network Graph', abbreviation: 'NG' },
  { id: 'metrics', label: 'Time-Series', abbreviation: 'TS' },
  { id: 'scenarios', label: 'Scenario Builder', abbreviation: 'SB' },
];

export function SidebarNav() {
  const isSidebarCollapsed = useUIState((state) => state.isSidebarCollapsed);
  const toggleSidebar = useUIState((state) => state.toggleSidebar);

  const items = useMemo(() => NAVIGATION_ITEMS, []);

  return (
    <aside className={layoutStyles.sidebar} aria-label="Workspace primary navigation">
      <button
        type="button"
        onClick={toggleSidebar}
        className={layoutStyles.controlButton}
        aria-expanded={!isSidebarCollapsed}
      >
        {isSidebarCollapsed ? 'Expand' : 'Collapse'}
      </button>
      <nav className={layoutStyles.sidebarNav} aria-label="Primary">
        {items.map((item) => (
          <button
            key={item.id}
            className={layoutStyles.navButton}
            aria-current={item.status === 'active' ? 'page' : undefined}
          >
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                background: 'rgba(78, 160, 255, 0.16)',
                color: 'var(--color-text-primary)',
                fontWeight: 600,
                fontSize: '12px',
              }}
            >
              {item.abbreviation}
            </span>
            {!isSidebarCollapsed ? <span>{item.label}</span> : null}
          </button>
        ))}
      </nav>
    </aside>
  );
}
