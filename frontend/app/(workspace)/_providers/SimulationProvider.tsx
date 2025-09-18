'use client';

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  type ReactNode,
} from 'react';
import { useStoreWithEqualityFn } from 'zustand/traditional';
import { shallow } from 'zustand/shallow';
import { createStore } from 'zustand/vanilla';
import type { ScenarioSummary } from '@/lib/types/simulation';

export interface TimelineState {
  current: number;
  max: number;
  status: 'idle' | 'loading';
}

interface SimulationState {
  scenarioList: ScenarioSummary[];
  activeScenarioId: string | null;
  timeline: TimelineState;
  setScenarioList: (scenarios: ScenarioSummary[]) => void;
  setActiveScenario: (scenarioId: string | null) => void;
  setTimeline: (timeline: Partial<TimelineState>) => void;
}

export type SimulationStore = ReturnType<typeof createSimulationStore>;

const SimulationContext = createContext<SimulationStore | null>(null);

const defaultTimeline: TimelineState = {
  current: 0,
  max: 0,
  status: 'idle',
};

function createSimulationStore(initialState?: Partial<SimulationState>) {
  return createStore<SimulationState>((set) => ({
    scenarioList: initialState?.scenarioList ?? [],
    activeScenarioId: initialState?.activeScenarioId ?? null,
    timeline: initialState?.timeline ?? { ...defaultTimeline },
    setScenarioList: (scenarios) =>
      set((state) => ({
        scenarioList: scenarios,
        activeScenarioId: state.activeScenarioId ?? scenarios[0]?.id ?? null,
      })),
    setActiveScenario: (scenarioId) =>
      set(() => ({
        activeScenarioId: scenarioId,
      })),
    setTimeline: (timeline) =>
      set((state) => ({
        timeline: { ...state.timeline, ...timeline },
      })),
  }));
}

interface SimulationProviderProps {
  children: ReactNode;
  initialScenarioList?: ScenarioSummary[];
  initialActiveScenarioId?: string | null;
}

export function SimulationProvider({
  children,
  initialScenarioList,
  initialActiveScenarioId,
}: SimulationProviderProps) {
  const storeRef = useRef<SimulationStore>();

  if (!storeRef.current) {
    storeRef.current = createSimulationStore({
      scenarioList: initialScenarioList,
      activeScenarioId: initialActiveScenarioId ?? initialScenarioList?.[0]?.id ?? null,
    });
  }

  const store = storeRef.current;

  useEffect(() => {
    if (initialScenarioList && initialScenarioList.length > 0) {
      store.setState((state) => ({
        ...state,
        scenarioList: initialScenarioList,
        activeScenarioId: state.activeScenarioId ?? initialScenarioList[0]?.id ?? null,
      }));
    }
  }, [store, initialScenarioList]);

  useEffect(() => {
    if (initialActiveScenarioId) {
      store.setState((state) => ({
        ...state,
        activeScenarioId: initialActiveScenarioId,
      }));
    }
  }, [store, initialActiveScenarioId]);

  return (
    <SimulationContext.Provider value={store}>{children}</SimulationContext.Provider>
  );
}

export function useSimulationStore<T>(selector: (state: SimulationState) => T): T {
  const store = useContext(SimulationContext);
  if (!store) {
    throw new Error('useSimulationStore must be used within a SimulationProvider');
  }

  return useStoreWithEqualityFn(store, selector, shallow);
}

export function useSimulationActions() {
  const store = useContext(SimulationContext);
  if (!store) {
    throw new Error('useSimulationActions must be used within a SimulationProvider');
  }

  const setScenarioList = useMemo(() => store.getState().setScenarioList, [store]);
  const setActiveScenario = useMemo(() => store.getState().setActiveScenario, [store]);
  const setTimeline = useMemo(() => store.getState().setTimeline, [store]);

  return { setScenarioList, setActiveScenario, setTimeline };
}
