"use client";

import { useMemo } from "react";
import { useSimulationState } from "@/lib/state/SimulationStateContext";
import styles from "./TimelinePanel.module.css";

function formatDate(value: string | undefined): string {
  if (!value) return "";
  const date = new Date(value);
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

export function TimelinePanel(): JSX.Element {
  const { timeline, setCurrentStepIndex, currentStep } = useSimulationState();
  const steps = timeline.steps;
  const currentIndex = timeline.currentIndex;

  const fieldChanges = useMemo(() => currentStep?.audit.field_changes ?? [], [currentStep]);

  return (
    <section className={styles.panel}>
      <header className={styles.header}>
        <div>
          <h2>Simulation Timeline</h2>
          <p>
            Scrub through reducer outputs and audit deltas. Current timestep: {" "}
            <strong>{currentStep?.timestep ?? "—"}</strong>
          </p>
        </div>
        <div className={styles.timelineMeta}>
          <span>{steps.length} recorded steps</span>
          {currentStep && <span>Captured {formatDate(currentStep.created_at)}</span>}
        </div>
      </header>
      <div className={styles.sliderRow}>
        <input
          type="range"
          min={0}
          max={Math.max(steps.length - 1, 0)}
          value={currentIndex}
          onChange={(event) => setCurrentStepIndex(Number(event.target.value))}
          className={styles.slider}
        />
        <div className={styles.marks}>
          {steps.map((step, index) => (
            <button
              key={step.id}
              type="button"
              className={`${styles.mark} ${index === currentIndex ? styles.markActive : ""}`}
              onClick={() => setCurrentStepIndex(index)}
            >
              <span>{step.timestep}</span>
              <small>{formatDate(step.created_at)}</small>
            </button>
          ))}
        </div>
      </div>
      <div className={styles.deltas}>
        <div>
          <h3>Key Field Changes</h3>
          {fieldChanges.length === 0 && <p className={styles.empty}>No changes recorded.</p>}
          <ul className={styles.deltaList}>
            {fieldChanges.slice(0, 6).map((change) => (
              <li key={change.field_path}>
                <div>
                  <strong>{change.field_path}</strong>
                  <p className={styles.deltaMeta}>Reducer: {change.reducer_name}</p>
                </div>
                <div className={styles.deltaValues}>
                  <span>{String(change.old_value ?? "∅")}</span>
                  <span className={styles.arrow}>→</span>
                  <span>{String(change.new_value ?? "∅")}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className={styles.auditSummary}>
          <h3>Audit Summary</h3>
          <ul>
            <li>
              <span>Reducers executed</span>
              <strong>{currentStep?.audit.reducer_sequence.length ?? 0}</strong>
            </li>
            <li>
              <span>Triggers fired</span>
              <strong>{currentStep?.audit.triggers_fired.length ?? 0}</strong>
            </li>
            <li>
              <span>Errors logged</span>
              <strong>{currentStep?.audit.errors.length ?? 0}</strong>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
