"use client";

import { MapView } from "@/components/map/MapView";
import { EvidenceRail } from "@/components/map/evidence/EvidenceRail";
import styles from "./MapPanel.module.css";

export function MapPanel(): JSX.Element {
  return (
    <section className={styles.panel}>
      <div className={styles.mapContainer}>
        <MapView />
        <EvidenceRail />
      </div>
    </section>
  );
}
