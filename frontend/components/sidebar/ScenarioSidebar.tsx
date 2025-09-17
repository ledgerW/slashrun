"use client";

import { useSimulationState } from "@/lib/state/SimulationStateContext";
import styles from "./ScenarioSidebar.module.css";

export function ScenarioSidebar(): JSX.Element {
  const { scenarios, activeScenario, setActiveScenario } = useSimulationState();

  return (
    <aside className={styles.sidebar}>
      <header className={styles.header}>
        <h2 className={styles.title}>Scenarios</h2>
        <span className="status-pill status-pill--active">
          {scenarios.length} available
        </span>
      </header>
      <div className={styles.listWrapper}>
        <ul className="list-reset">
          {scenarios.map((scenario) => {
            const isActive = scenario.id === activeScenario?.id;
            return (
              <li key={scenario.id}>
                <button
                  type="button"
                  className={`${styles.scenarioItem} ${
                    isActive ? styles.active : ""
                  }`}
                  onClick={() => setActiveScenario(scenario.id)}
                >
                  <div className={styles.itemHeader}>
                    <span className={styles.scenarioName}>{scenario.name}</span>
                    {isActive ? (
                      <span className="tag">
                        <span className="badge-dot" aria-hidden /> Active
                      </span>
                    ) : (
                      <span className={styles.turnCount}>t={scenario.currentTimestep}</span>
                    )}
                  </div>
                  <p className={styles.description}>{scenario.description}</p>
                  <div className={styles.metaRow}>
                    <span>{scenario.triggersCount} triggers</span>
                    <span>
                      Updated {new Date(scenario.updatedAt).toLocaleDateString()}
                    </span>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </aside>
  );
}
