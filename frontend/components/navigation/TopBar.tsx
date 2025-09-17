"use client";

import { useSimulationState } from "@/lib/state/SimulationStateContext";
import styles from "./TopBar.module.css";

export function TopBar(): JSX.Element {
  const {
    scenarios,
    activeScenario,
    currentStep,
    isLoading,
    refreshActiveScenario,
    advanceSimulation,
  } = useSimulationState();

  return (
    <header className={styles.header}>
      <div className={styles.leftGroup}>
        <h1 className={styles.title}>SlashRun Control Tower</h1>
        <div className={styles.meta}>
          <span className={styles.metaItem}>
            Active Scenario:
            <strong>{activeScenario?.name ?? "No scenario selected"}</strong>
          </span>
          <span className={styles.metaItem}>
            Timestep: <strong>{currentStep?.timestep ?? "—"}</strong>
          </span>
          <span className={`${styles.metaItem} ${styles.metaItemMuted}`}>
            {scenarios.length} scenarios loaded
          </span>
        </div>
      </div>
      <div className={styles.actionGroup}>
        <button
          className="action-btn"
          type="button"
          onClick={refreshActiveScenario}
          disabled={!activeScenario || isLoading}
        >
          <span className="badge-dot" aria-hidden /> Refresh state
        </button>
        <button
          className="action-btn"
          type="button"
          onClick={advanceSimulation}
          disabled={!activeScenario || isLoading}
        >
          Step simulation
        </button>
      </div>
    </header>
  );
}
