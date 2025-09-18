'use client';

import layoutStyles from '@/styles/layout.module.css';

export function WorkspaceLoadingState() {
  return (
    <div className={layoutStyles.workspaceShell} aria-busy="true">
      <aside className={layoutStyles.sidebar} aria-hidden>
        <SidebarSkeleton />
      </aside>
      <header className={layoutStyles.topBar} />
      <main className={layoutStyles.mainCanvas}>
        <div
          style={{
            display: 'grid',
            gap: 'var(--space-5)',
          }}
        >
          <SkeletonBlock height="160px" />
          <SkeletonBlock height="200px" />
          <SkeletonBlock height="140px" />
        </div>
      </main>
      <div className={layoutStyles.evidenceRail} aria-hidden />
      <footer className={layoutStyles.timelineFooter} aria-hidden />
    </div>
  );
}

function SidebarSkeleton() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
      }}
    >
      <SkeletonBlock height="48px" />
      <SkeletonBlock height="48px" />
      <SkeletonBlock height="48px" />
    </div>
  );
}

function SkeletonBlock({ height }: { height: string }) {
  return (
    <div
      style={{
        height,
        borderRadius: 'var(--radius-md)',
        background:
          'linear-gradient(135deg, rgba(26, 36, 54, 0.9) 0%, rgba(18, 24, 36, 0.65) 100%)',
        border: '1px solid rgba(78, 160, 255, 0.12)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'linear-gradient(90deg, transparent 0%, rgba(78, 160, 255, 0.18) 50%, transparent 100%)',
          transform: 'translateX(-100%)',
          animation: 'loading-shimmer 1.6s ease-in-out infinite',
        }}
      />
    </div>
  );
}
