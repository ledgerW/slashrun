'use client';

import type { ReactNode } from 'react';
import layoutStyles from '@/styles/layout.module.css';
import { cn } from '@/lib/utils';
import { useUIState } from '../_providers/UIStateProvider';
import { EvidenceRail } from './EvidenceRail';
import { SidebarNav } from './SidebarNav';
import { TimelineFooter } from './TimelineFooter';
import { TopBar } from './TopBar';

interface WorkspaceShellProps {
  children: ReactNode;
}

export function WorkspaceShell({ children }: WorkspaceShellProps) {
  const isSidebarCollapsed = useUIState((state) => state.isSidebarCollapsed);
  const isTimelineCollapsed = useUIState((state) => state.isTimelineCollapsed);

  return (
    <div
      className={cn(
        layoutStyles.workspaceShell,
        isSidebarCollapsed && layoutStyles.workspaceShellCollapsed,
      )}
    >
      <a href="#workspace-main" className={layoutStyles.skipLink}>
        Skip to main content
      </a>
      <SidebarNav />
      <TopBar />
      <main
        id="workspace-main"
        className={layoutStyles.mainCanvas}
        tabIndex={-1}
        role="main"
      >
        {children}
      </main>
      <EvidenceRail />
      <TimelineFooter
        className={cn(isTimelineCollapsed && layoutStyles.timelineFooterHidden)}
      />
    </div>
  );
}
