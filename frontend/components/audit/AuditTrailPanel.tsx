"use client";

import { useMemo } from "react";
import { useSimulationState } from "@/lib/state/SimulationStateContext";
import styles from "./AuditTrailPanel.module.css";

export function AuditTrailPanel(): JSX.Element {
  const { currentStep } = useSimulationState();

  const fieldChanges = useMemo(() => currentStep?.audit.field_changes ?? [], [currentStep]);
  const errors = currentStep?.audit.errors ?? [];

  return (
    <section className={styles.panel}>
      <header className={styles.header}>
        <h2>Audit Trail</h2>
        <p>Reducer transparency, trigger execution, and error diagnostics.</p>
      </header>
      <div className={styles.content}>
        <div className={styles.changes}>
          <h3>Field Changes</h3>
          {fieldChanges.length === 0 ? (
            <p className={styles.empty}>No changes captured for this step.</p>
          ) : (
            <ul className={styles.changeList}>
              {fieldChanges.slice(0, 5).map((change) => (
                <li key={change.field_path}>
                  <div>
                    <strong>{change.field_path}</strong>
                    <p className={styles.reducerMeta}>{change.reducer_name}</p>
                  </div>
                  <div className={styles.changeValues}>
                    <span>{String(change.old_value ?? "∅")}</span>
                    <span className={styles.arrow}>→</span>
                    <span>{String(change.new_value ?? "∅")}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className={styles.diagnostics}>
          <h3>Diagnostics</h3>
          <div className={styles.diagnosticGrid}>
            <div>
              <span className={styles.label}>Triggers Fired</span>
              <strong>{currentStep?.audit.triggers_fired.length ?? 0}</strong>
            </div>
            <div>
              <span className={styles.label}>Reducer Sequence</span>
              <strong>{currentStep?.audit.reducer_sequence.length ?? 0}</strong>
            </div>
            <div>
              <span className={styles.label}>Errors</span>
              <strong className={errors.length > 0 ? styles.errorCount : ""}>
                {errors.length}
              </strong>
            </div>
          </div>
          {errors.length > 0 && (
            <ul className={styles.errorList}>
              {errors.map((error) => (
                <li key={error}>{error}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}
