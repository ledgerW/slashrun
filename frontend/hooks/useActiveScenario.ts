'use client';

import { useCallback, useEffect, useMemo } from 'react';
import { ACTIVE_SCENARIO_STORAGE_KEY } from '@/lib/constants';
import { useSimulationActions, useSimulationStore } from '@/providers/SimulationProvider';
import type { ScenarioSummary } from '@/lib/types/simulation';

function getStoredScenarioId(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  return window.localStorage.getItem(ACTIVE_SCENARIO_STORAGE_KEY);
}

export function useActiveScenario() {
  const scenarioList = useSimulationStore((state) => state.scenarioList);
  const activeScenarioId = useSimulationStore((state) => state.activeScenarioId);
  const { setActiveScenario } = useSimulationActions();

  useEffect(() => {
    const storedId = getStoredScenarioId();
    if (!storedId) {
      if (!activeScenarioId && scenarioList.length > 0) {
        setActiveScenario(scenarioList[0]?.id ?? null);
      }
      return;
    }

    const storedScenarioExists = scenarioList.some((scenario) => scenario.id === storedId);
    if (storedScenarioExists && storedId !== activeScenarioId) {
      setActiveScenario(storedId);
    }
  }, [scenarioList, activeScenarioId, setActiveScenario]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    if (activeScenarioId) {
      window.localStorage.setItem(ACTIVE_SCENARIO_STORAGE_KEY, activeScenarioId);
    }
  }, [activeScenarioId]);

  const updateActiveScenario = useCallback(
    (scenarioId: string | null) => {
      setActiveScenario(scenarioId);
      if (typeof window !== 'undefined') {
        if (scenarioId) {
          window.localStorage.setItem(ACTIVE_SCENARIO_STORAGE_KEY, scenarioId);
        } else {
          window.localStorage.removeItem(ACTIVE_SCENARIO_STORAGE_KEY);
        }
      }
    },
    [setActiveScenario],
  );

  const activeScenario = useMemo<ScenarioSummary | null>(() => {
    if (!activeScenarioId) {
      return null;
    }
    return scenarioList.find((scenario) => scenario.id === activeScenarioId) ?? null;
  }, [scenarioList, activeScenarioId]);

  return {
    scenarioList,
    activeScenarioId,
    activeScenario,
    setActiveScenario: updateActiveScenario,
  };
}
