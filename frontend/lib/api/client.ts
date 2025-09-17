import type {
  ScenarioDetail,
  ScenarioSummary,
  SimulationStep,
} from "@/types/simulation";
import { mockScenarioDetails, mockScenarioSummaries } from "@/lib/mocks/mockState";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api";

async function fetchJson<T>(endpoint: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export async function loadScenarioSummaries(): Promise<ScenarioSummary[]> {
  if (!isBrowser()) {
    return mockScenarioSummaries;
  }

  try {
    const data = await fetchJson<ScenarioSummary[]>("/simulation/scenarios");
    if (!Array.isArray(data) || data.length === 0) {
      return mockScenarioSummaries;
    }
    return data;
  } catch (error) {
    console.warn("Falling back to mock scenario summaries", error);
    return mockScenarioSummaries;
  }
}

export async function loadScenarioDetail(id: string): Promise<ScenarioDetail> {
  if (!isBrowser()) {
    return mockScenarioDetails[id];
  }

  try {
    const data = await fetchJson<ScenarioDetail>(`/simulation/scenarios/${id}`);
    return data;
  } catch (error) {
    console.warn(`Falling back to mock scenario detail for ${id}`, error);
    const fallback = mockScenarioDetails[id];
    if (!fallback) {
      throw error;
    }
    return fallback;
  }
}

export async function stepScenario(id: string): Promise<SimulationStep> {
  if (!isBrowser()) {
    const detail = mockScenarioDetails[id];
    const nextStep = detail.history[detail.history.length - 1];
    return nextStep;
  }

  try {
    return await fetchJson<SimulationStep>(`/simulation/scenarios/${id}/step`, {
      method: "POST",
    });
  } catch (error) {
    console.warn(`Step simulation fallback for ${id}`, error);
    const detail = mockScenarioDetails[id];
    return detail.history[detail.history.length - 1];
  }
}
