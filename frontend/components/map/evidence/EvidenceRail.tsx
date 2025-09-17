"use client";

import { useMemo } from "react";
import { useSimulationState } from "@/lib/state/SimulationStateContext";
import styles from "./EvidenceRail.module.css";

interface EvidenceEvent {
  id?: string;
  type?: string;
  description?: string;
  eta?: string;
  applied_at?: string;
}

export function EvidenceRail(): JSX.Element {
  const { currentState, currentStep } = useSimulationState();

  const pendingEvents = useMemo(() => {
    const events = currentState?.events?.pending ?? [];
    return events.slice(0, 4) as EvidenceEvent[];
  }, [currentState]);

  const processedEvents = useMemo(() => {
    const events = currentState?.events?.processed ?? [];
    return events.slice(-4) as EvidenceEvent[];
  }, [currentState]);

  const reducerChain = currentStep?.audit.reducer_sequence ?? [];
  const triggers = currentStep?.audit.triggers_fired ?? [];

  return (
    <div className={styles.container}>
      <section>
        <h4 className={styles.sectionTitle}>Reducer Chain</h4>
        <ol className={styles.sequence}>
          {reducerChain.map((name, index) => (
            <li key={name}>
              <span className={styles.stepIndex}>{index + 1}</span>
              <div>
                <strong>{name}</strong>
                <p className={styles.stepMeta}>Completed</p>
              </div>
            </li>
          ))}
          {reducerChain.length === 0 && <p className={styles.empty}>No reducers executed.</p>}
        </ol>
      </section>
      <div className="subtle-divider" />
      <section>
        <h4 className={styles.sectionTitle}>Pending Events</h4>
        <ul className={styles.eventList}>
          {pendingEvents.map((event) => (
            <li key={event.id ?? event.description} className={styles.eventItem}>
              <span className="tag">{event.type}</span>
              <p>{event.description}</p>
              {event.eta && <span className={styles.eventMeta}>ETA {event.eta}</span>}
            </li>
          ))}
          {pendingEvents.length === 0 && <p className={styles.empty}>No pending events</p>}
        </ul>
      </section>
      <div className="subtle-divider" />
      <section>
        <h4 className={styles.sectionTitle}>Recent Events</h4>
        <ul className={styles.eventList}>
          {processedEvents.map((event) => (
            <li key={event.id ?? event.description} className={styles.eventItem}>
              <span className="tag tag--danger">{event.type}</span>
              <p>{event.description}</p>
              {event.applied_at && (
                <span className={styles.eventMeta}>Applied {event.applied_at}</span>
              )}
            </li>
          ))}
          {processedEvents.length === 0 && <p className={styles.empty}>No recent events</p>}
        </ul>
      </section>
      {triggers.length > 0 && (
        <>
          <div className="subtle-divider" />
          <section>
            <h4 className={styles.sectionTitle}>Triggers Fired</h4>
            <ul className={styles.triggerList}>
              {triggers.map((trigger) => (
                <li key={trigger}>{trigger}</li>
              ))}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}
