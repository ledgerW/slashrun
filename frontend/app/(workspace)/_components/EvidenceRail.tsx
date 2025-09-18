'use client';

import layoutStyles from '@/styles/layout.module.css';
import { Panel } from './Panel';

export function EvidenceRail() {
  return (
    <aside className={layoutStyles.evidenceRail} aria-label="Evidence rail">
      <h2 className="label" style={{ margin: 0 }}>
        Evidence Feed
      </h2>
      <Panel title="Reducer Chain" subtitle="Last updated 12m ago">
        <ol
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-2)',
            paddingLeft: 'var(--space-4)',
            margin: 0,
          }}
        >
          <li>Sanctions intensity increased to Level 3.</li>
          <li>FX reserve depletion trigger armed.</li>
          <li>Energy export tariff variance beyond threshold.</li>
        </ol>
      </Panel>
      <Panel title="Alerts" subtitle="Operational signals">
        <ul
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-2)',
            paddingLeft: 'var(--space-4)',
            margin: 0,
          }}
        >
          <li>🚨 Central bank liquidity swap pending approval.</li>
          <li>⚠️ Supply chain latency spike across Baltic corridor.</li>
          <li>ℹ️ IMF envoy en route to coordination cell.</li>
        </ul>
      </Panel>
    </aside>
  );
}
