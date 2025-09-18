'use client';

import { useEffect, type ReactNode } from 'react';
import layoutStyles from '@/styles/layout.module.css';
import { cn } from '@/lib/utils';
import { useUIState } from '../_providers/UIStateProvider';
import { useSimulationActions } from '@/providers/SimulationProvider';
import type { ScenarioSummary } from '@/lib/types/simulation';
import { EvidenceRail } from './EvidenceRail';
import { SidebarNav } from './SidebarNav';
import { TimelineFooter } from './TimelineFooter';
import { TopBar } from './TopBar';

interface WorkspaceShellProps {
  children: ReactNode;
  initialScenarioList?: ScenarioSummary[];
  initialActiveScenarioId?: string | null;
}

export function WorkspaceShell({
  children,
  initialScenarioList,
  initialActiveScenarioId,
}: WorkspaceShellProps) {
  const isSidebarCollapsed = useUIState((state) => state.isSidebarCollapsed);
  const isTimelineCollapsed = useUIState((state) => state.isTimelineCollapsed);
  const { setScenarioList, setActiveScenario } = useSimulationActions();

  useEffect(() => {
    if (initialScenarioList && initialScenarioList.length > 0) {
      setScenarioList(initialScenarioList);
      if (initialActiveScenarioId) {
        setActiveScenario(initialActiveScenarioId);
      }
    }
  }, [initialScenarioList, initialActiveScenarioId, setScenarioList, setActiveScenario]);

  useEffect(() => {
    const main = document.getElementById('workspace-main');
    main?.focus();
  }, []);

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
