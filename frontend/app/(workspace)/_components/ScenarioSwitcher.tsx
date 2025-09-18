'use client';

import { useEffect } from 'react';
import type { ChangeEvent } from 'react';
import { useScenarioList } from '@/hooks/useScenarioList';
import { useActiveScenario } from '@/hooks/useActiveScenario';
import { useSimulationActions } from '@/providers/SimulationProvider';

export function ScenarioSwitcher() {
  const { data: scenarios, isLoading } = useScenarioList();
  const { activeScenarioId, setActiveScenario } = useActiveScenario();
  const { setScenarioList } = useSimulationActions();

  useEffect(() => {
    if (scenarios) {
      setScenarioList(scenarios);
    }
  }, [scenarios, setScenarioList]);

  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setActiveScenario(event.target.value);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      <label htmlFor="scenario-switcher" className="label">
        Scenario
      </label>
      <select
        id="scenario-switcher"
        name="scenario-switcher"
        onChange={handleChange}
        value={activeScenarioId ?? ''}
        disabled={isLoading || !scenarios?.length}
        style={{
          background: 'rgba(16, 24, 38, 0.85)',
          border: '1px solid rgba(78, 160, 255, 0.25)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--color-text-primary)',
          padding: '12px 16px',
          minWidth: '220px',
        }}
      >
        {scenarios?.length ? (
          scenarios.map((scenario) => (
            <option key={scenario.id} value={scenario.id}>
              {scenario.name}
            </option>
          ))
        ) : (
          <option value="" disabled>
            {isLoading ? 'Loading scenarios…' : 'No scenarios available'}
          </option>
        )}
      </select>
    </div>
  );
}
