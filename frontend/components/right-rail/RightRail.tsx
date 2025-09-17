"use client";

import { CountryMetricsPanel } from "@/components/insights/CountryMetricsPanel";
import { NetworkSummaryPanel } from "@/components/insights/NetworkSummaryPanel";
import { AuditTrailPanel } from "@/components/audit/AuditTrailPanel";
import styles from "./RightRail.module.css";

export function RightRail(): JSX.Element {
  return (
    <aside className={styles.rail}>
      <CountryMetricsPanel />
      <NetworkSummaryPanel />
      <AuditTrailPanel />
    </aside>
  );
}
