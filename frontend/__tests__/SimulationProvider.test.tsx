import React from 'react';
import { act, renderHook } from '@testing-library/react';
import { SimulationProvider, useSimulationActions, useSimulationStore } from '@/providers/SimulationProvider';
import type { ScenarioSummary } from '@/lib/types/simulation';

describe('SimulationProvider', () => {
  const scenarioAlpha: ScenarioSummary = {
    id: 'alpha',
    name: 'Alpha Scenario',
    description: 'First simulation',
    createdAt: '2024-01-01T00:00:00.000Z',
    updatedAt: '2024-01-02T00:00:00.000Z',
    triggersCount: 3,
    currentTimestep: 12,
  };

  const scenarioBeta: ScenarioSummary = {
    id: 'beta',
    name: 'Beta Scenario',
    description: null,
    createdAt: '2024-02-01T00:00:00.000Z',
    updatedAt: '2024-02-02T00:00:00.000Z',
    triggersCount: 5,
    currentTimestep: 4,
  };

  it('initialises store with provided scenarios and active id', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <SimulationProvider initialScenarioList={[scenarioAlpha]} initialActiveScenarioId="alpha">
        {children}
      </SimulationProvider>
    );

    const { result } = renderHook(
      () =>
        useSimulationStore((state) => ({
          scenarioList: state.scenarioList,
          activeScenarioId: state.activeScenarioId,
          timeline: state.timeline,
        })),
      { wrapper },
    );

    expect(result.current.scenarioList).toEqual([scenarioAlpha]);
    expect(result.current.activeScenarioId).toBe('alpha');
    expect(result.current.timeline).toEqual({ current: 0, max: 0, status: 'idle' });
  });

  it('updates scenario list and defaults active scenario when none provided', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <SimulationProvider>{children}</SimulationProvider>
    );

    const { result } = renderHook(
      () => ({
        state: useSimulationStore((state) => ({
          scenarioList: state.scenarioList,
          activeScenarioId: state.activeScenarioId,
        })),
        actions: useSimulationActions(),
      }),
      { wrapper },
    );

    act(() => {
      result.current.actions.setScenarioList([scenarioAlpha, scenarioBeta]);
    });

    expect(result.current.state.scenarioList).toHaveLength(2);
    expect(result.current.state.activeScenarioId).toBe('alpha');
  });

  it('allows manually setting active scenario', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <SimulationProvider initialScenarioList={[scenarioAlpha, scenarioBeta]}>{children}</SimulationProvider>
    );

    const { result } = renderHook(
      () => ({
        state: useSimulationStore((state) => ({
          scenarioList: state.scenarioList,
          activeScenarioId: state.activeScenarioId,
        })),
        actions: useSimulationActions(),
      }),
      { wrapper },
    );

    act(() => {
      result.current.actions.setActiveScenario('beta');
    });

    expect(result.current.state.activeScenarioId).toBe('beta');
  });

  it('merges timeline updates', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <SimulationProvider>{children}</SimulationProvider>
    );

    const { result } = renderHook(
      () => ({
        timeline: useSimulationStore((state) => state.timeline),
        actions: useSimulationActions(),
      }),
      { wrapper },
    );

    act(() => {
      result.current.actions.setTimeline({ current: 5, max: 20, status: 'loading' });
    });

    expect(result.current.timeline).toEqual({ current: 5, max: 20, status: 'loading' });

    act(() => {
      result.current.actions.setTimeline({ status: 'idle' });
    });

    expect(result.current.timeline).toEqual({ current: 5, max: 20, status: 'idle' });
  });
});
