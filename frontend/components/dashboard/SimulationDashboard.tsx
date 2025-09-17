"use client";

import { useMemo } from "react";
import { SimulationStateProvider } from "@/lib/state/SimulationStateContext";
import { TopBar } from "@/components/navigation/TopBar";
import { ScenarioSidebar } from "@/components/sidebar/ScenarioSidebar";
import { MapPanel } from "@/components/map/MapPanel";
import { TimelinePanel } from "@/components/timeline/TimelinePanel";
import { RightRail } from "@/components/right-rail/RightRail";
import styles from "./SimulationDashboard.module.css";

export function SimulationDashboard(): JSX.Element {
  const gridTemplate = useMemo(
    () => ({
      gridTemplateColumns: "320px minmax(0, 1fr) 360px",
    }),
    []
  );

  return (
    <SimulationStateProvider>
      <div className={styles.wrapper}>
        <TopBar />
        <main className={styles.main} style={gridTemplate}>
          <ScenarioSidebar />
          <section className={styles.workspace}>
            <MapPanel />
            <TimelinePanel />
          </section>
          <RightRail />
        </main>
      </div>
    </SimulationStateProvider>
  );
}

export default SimulationDashboard;
