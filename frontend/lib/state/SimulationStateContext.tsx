"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type {
  CountryState,
  GlobalState,
  ScenarioDetail,
  ScenarioSummary,
  SimulationStep,
} from "@/types/simulation";
import {
  loadScenarioDetail,
  loadScenarioSummaries,
  stepScenario,
} from "@/lib/api/client";

interface CountryEntry {
  id: string;
  state: CountryState;
}

interface SimulationStateContextValue {
  scenarios: ScenarioSummary[];
  activeScenario: ScenarioDetail | undefined;
  currentStep: SimulationStep | undefined;
  currentState: GlobalState | undefined;
  timeline: { steps: SimulationStep[]; currentIndex: number };
  setCurrentStepIndex: (index: number) => void;
  setActiveScenario: (id: string) => void;
  refreshActiveScenario: () => Promise<void>;
  advanceSimulation: () => Promise<void>;
  isLoading: boolean;
  selectedCountryId: string | null;
  selectedCountry: CountryState | undefined;
  setSelectedCountry: (id: string | null) => void;
  countries: CountryEntry[];
}

const SimulationStateContext = createContext<SimulationStateContextValue | undefined>(
  undefined
);

export function SimulationStateProvider({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [details, setDetails] = useState<Record<string, ScenarioDetail>>({});
  const [activeScenarioId, setActiveScenarioId] = useState<string | null>(null);
  const [timelineIndex, setTimelineIndex] = useState<number>(0);
  const [selectedCountryId, setSelectedCountryId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    let cancelled = false;
    loadScenarioSummaries().then((loaded) => {
      if (cancelled) return;
      setScenarios(loaded);
      if (!activeScenarioId && loaded.length > 0) {
        setActiveScenarioId(loaded[0].id);
      }
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!activeScenarioId) {
      return;
    }
    let cancelled = false;
    setIsLoading(true);
    loadScenarioDetail(activeScenarioId)
      .then((detail) => {
        if (cancelled) return;
        setDetails((prev) => ({
          ...prev,
          [detail.id]: detail,
        }));
        const newIndex = Math.max(detail.history.length - 1, 0);
        setTimelineIndex(newIndex);
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeScenarioId]);

  const activeScenario = activeScenarioId ? details[activeScenarioId] : undefined;

  const timelineSteps = useMemo(
    () => activeScenario?.history ?? [],
    [activeScenario]
  );
  const currentStep =
    timelineSteps.length > 0
      ? timelineSteps[Math.min(timelineIndex, timelineSteps.length - 1)]
      : undefined;

  const currentState: GlobalState | undefined = currentStep
    ? currentStep.state
    : activeScenario?.current_state;

  useEffect(() => {
    if (!currentState) {
      setSelectedCountryId(null);
      return;
    }
    if (selectedCountryId && currentState.countries[selectedCountryId]) {
      return;
    }
    const firstCountryId = Object.keys(currentState.countries)[0];
    if (firstCountryId) {
      setSelectedCountryId(firstCountryId);
    }
  }, [currentState, selectedCountryId]);

  const countries: CountryEntry[] = useMemo(() => {
    if (!currentState) return [];
    return Object.entries(currentState.countries).map(([id, state]) => ({ id, state }));
  }, [currentState]);

  const selectedCountry = useMemo(() => {
    if (!selectedCountryId || !currentState) {
      return undefined;
    }
    return currentState.countries[selectedCountryId];
  }, [currentState, selectedCountryId]);

  const setCurrentStepIndex = useCallback(
    (index: number) => {
      if (!activeScenario) {
        return;
      }
      const safeIndex = Math.max(0, Math.min(index, activeScenario.history.length - 1));
      setTimelineIndex(safeIndex);
    },
    [activeScenario]
  );

  const setActiveScenario = useCallback((id: string) => {
    setActiveScenarioId(id);
  }, []);

  const refreshActiveScenario = useCallback(async () => {
    if (!activeScenarioId) return;
    setIsLoading(true);
    try {
      const detail = await loadScenarioDetail(activeScenarioId);
      setDetails((prev) => ({
        ...prev,
        [detail.id]: detail,
      }));
      const newIndex = Math.max(detail.history.length - 1, 0);
      setTimelineIndex(newIndex);
    } finally {
      setIsLoading(false);
    }
  }, [activeScenarioId]);

  const advanceSimulation = useCallback(async () => {
    if (!activeScenarioId) return;
    setIsLoading(true);
    try {
      const step = await stepScenario(activeScenarioId);
      setDetails((prev) => {
        const existing = prev[activeScenarioId];
        if (!existing) {
          return prev;
        }
        const history = [...existing.history, step];
        setTimelineIndex(history.length - 1);
        return {
          ...prev,
          [activeScenarioId]: {
            ...existing,
            current_timestep: step.timestep,
            current_state: step.state,
            history,
          },
        };
      });
    } finally {
      setIsLoading(false);
    }
  }, [activeScenarioId]);

  const value = useMemo<SimulationStateContextValue>(() => ({
    scenarios,
    activeScenario,
    currentStep,
    currentState,
    timeline: { steps: timelineSteps, currentIndex: timelineIndex },
    setCurrentStepIndex,
    setActiveScenario,
    refreshActiveScenario,
    advanceSimulation,
    isLoading,
    selectedCountryId,
    selectedCountry,
    setSelectedCountry: setSelectedCountryId,
    countries,
  }), [
    scenarios,
    activeScenario,
    currentStep,
    currentState,
    timelineSteps,
    timelineIndex,
    setCurrentStepIndex,
    setActiveScenario,
    refreshActiveScenario,
    advanceSimulation,
    isLoading,
    selectedCountryId,
    selectedCountry,
    countries,
  ]);

  return (
    <SimulationStateContext.Provider value={value}>
      {children}
    </SimulationStateContext.Provider>
  );
}

export function useSimulationState(): SimulationStateContextValue {
  const context = useContext(SimulationStateContext);
  if (!context) {
    throw new Error("useSimulationState must be used within SimulationStateProvider");
  }
  return context;
}
