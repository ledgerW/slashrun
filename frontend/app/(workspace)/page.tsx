import type { CSSProperties } from 'react';
import { Panel } from './_components/Panel';

const gridItemStyle: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
};

export default function WorkspaceHome() {
  return (
    <>
      <Panel title="Operational Posture" subtitle="Live from Crisis Room Delta">
        <div style={gridItemStyle}>
          <p>
            The baseline simulation indicates a{' '}
            <strong style={{ color: 'var(--color-positive)' }}>12% uplift</strong> in
            coalition cohesion scores following the latest diplomatic interventions.
          </p>
          <p>
            Monitor energy corridors for volatility and prepare contingency responses for
            retaliatory trade actions.
          </p>
        </div>
      </Panel>
      <Panel title="Key Indicators" subtitle="Signals aligned to horizon scanning">
        <ul
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: 'var(--space-4)',
            margin: 0,
            padding: 0,
            listStyle: 'none',
          }}
        >
          <li>
            <span className="label">FX Reserves</span>
            <p
              style={{ color: 'var(--color-text-primary)', fontSize: '24px', margin: 0 }}
            >
              $458B
            </p>
            <small style={{ color: 'var(--color-positive)' }}>
              +3.4% vs last timestep
            </small>
          </li>
          <li>
            <span className="label">Trade Flow</span>
            <p
              style={{ color: 'var(--color-text-primary)', fontSize: '24px', margin: 0 }}
            >
              72.4
            </p>
            <small style={{ color: 'var(--color-warning)' }}>-1.8% vs baseline</small>
          </li>
          <li>
            <span className="label">Sentiment</span>
            <p
              style={{ color: 'var(--color-text-primary)', fontSize: '24px', margin: 0 }}
            >
              Neutral
            </p>
            <small style={{ color: 'var(--color-text-muted)' }}>Stable</small>
          </li>
        </ul>
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
    </>
  );
}
