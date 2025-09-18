import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import type { CSSProperties } from 'react';
import { getUserSession } from '@/lib/auth';
import { fetchScenarioSummaries } from '@/lib/simulation';
import { scenarioListQueryKey } from '@/lib/query/scenarios';
import { WorkspaceShell } from './_components/WorkspaceShell';
import { Panel } from './_components/Panel';

const listStyle: CSSProperties = {
  display: 'grid',
  gap: 'var(--space-3)',
  margin: 0,
  padding: 0,
  listStyle: 'none',
};

export default async function WorkspaceHome() {
  const user = await getUserSession();
  const queryClient = new QueryClient();
  const scenarios = await fetchScenarioSummaries();
  const scenarioKey = scenarioListQueryKey(user?.id ?? null);
  queryClient.setQueryData(scenarioKey, scenarios);

  const activeScenarioId = scenarios[0]?.id ?? null;

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <WorkspaceShell
        initialScenarioList={scenarios}
        initialActiveScenarioId={activeScenarioId}
      >
        <Panel
          title="Scenario Briefings"
          subtitle="Latest operational sims available to your desk"
        >
          <ul style={listStyle}>
            {scenarios.map((scenario) => (
              <li
                key={scenario.id}
                style={{
                  padding: 'var(--space-3) var(--space-4)',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(20, 32, 52, 0.65)',
                  border: '1px solid rgba(78, 160, 255, 0.16)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <div>
                    <h3
                      style={{
                        margin: 0,
                        fontSize: '16px',
                        color: 'var(--color-text-primary)',
                      }}
                    >
                      {scenario.name}
                    </h3>
                    {scenario.description ? (
                      <p style={{ marginTop: '6px' }}>{scenario.description}</p>
                    ) : null}
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span className="label">Timestep</span>
                    <p
                      style={{
                        margin: 0,
                        fontSize: '24px',
                        color: 'var(--color-text-primary)',
                      }}
                    >
                      {scenario.currentTimestep}
                    </p>
                    <small style={{ color: 'var(--color-text-muted)' }}>
                      {scenario.triggersCount} triggers configured
                    </small>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </Panel>
        <Panel
          title="Key Indicators"
          subtitle="Signals aligned to horizon scanning"
        >
          <IndicatorsGrid />
        </Panel>
        <Panel title="Upcoming Tasks" subtitle="Investigative checklist">
          <ol
            style={{
              margin: 0,
              paddingLeft: 'var(--space-5)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-2)',
            }}
          >
            <li>Validate debt exposure triggers with finance cell.</li>
            <li>Upload satellite imagery overlays for Southeastern corridor.</li>
            <li>Review sanctions cascade modeling assumptions.</li>
          </ol>
        </Panel>
      </WorkspaceShell>
    </HydrationBoundary>
  );
}

function IndicatorsGrid() {
  return (
    <ul
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
        gap: 'var(--space-4)',
        margin: 0,
        padding: 0,
        listStyle: 'none',
      }}
    >
      <li>
        <span className="label">FX Reserves</span>
        <p style={{ color: 'var(--color-text-primary)', fontSize: '24px', margin: 0 }}>
          $458B
        </p>
        <small style={{ color: 'var(--color-positive)' }}>+3.4% vs last timestep</small>
      </li>
      <li>
        <span className="label">Trade Flow</span>
        <p style={{ color: 'var(--color-text-primary)', fontSize: '24px', margin: 0 }}>
          72.4
        </p>
        <small style={{ color: 'var(--color-warning)' }}>-1.8% vs baseline</small>
      </li>
      <li>
        <span className="label">Sentiment</span>
        <p style={{ color: 'var(--color-text-primary)', fontSize: '24px', margin: 0 }}>
          Neutral
        </p>
        <small style={{ color: 'var(--color-text-muted)' }}>Stable</small>
      </li>
    </ul>
  );
}
