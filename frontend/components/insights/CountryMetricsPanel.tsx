"use client";

import { useMemo } from "react";
import { useSimulationState } from "@/lib/state/SimulationStateContext";
import styles from "./CountryMetricsPanel.module.css";

export function CountryMetricsPanel(): JSX.Element {
  const { countries, selectedCountryId, selectedCountry, setSelectedCountry } =
    useSimulationState();

  const metrics = useMemo(() => {
    if (!selectedCountry) return [];
    return [
      {
        label: "GDP (USD tn)",
        value: selectedCountry.macro.gdp?.toFixed(2) ?? "—",
      },
      {
        label: "Potential GDP",
        value: selectedCountry.macro.potential_gdp?.toFixed(2) ?? "—",
      },
      {
        label: "Inflation",
        value: `${((selectedCountry.macro.inflation ?? 0) * 100).toFixed(2)}%`,
      },
      {
        label: "Unemployment",
        value: `${((selectedCountry.macro.unemployment ?? 0) * 100).toFixed(2)}%`,
      },
      {
        label: "Reserves (USD bn)",
        value: selectedCountry.external.reserves_usd?.toFixed(1) ?? "—",
      },
      {
        label: "Current Account",
        value: `${((selectedCountry.external.current_account_gdp ?? 0) * 100).toFixed(2)}%`,
      },
      {
        label: "Sovereign Yield",
        value: `${((selectedCountry.finance.sovereign_yield ?? 0) * 100).toFixed(2)}%`,
      },
      {
        label: "Credit Spread",
        value: `${((selectedCountry.finance.credit_spread ?? 0) * 100).toFixed(2)}%`,
      },
      {
        label: "Exports / GDP",
        value: `${((selectedCountry.trade.exports_gdp ?? 0) * 100).toFixed(1)}%`,
      },
      {
        label: "Imports / GDP",
        value: `${((selectedCountry.trade.imports_gdp ?? 0) * 100).toFixed(1)}%`,
      },
    ];
  }, [selectedCountry]);

  return (
    <section className={styles.panel}>
      <header className={styles.header}>
        <div>
          <h2>Country Metrics</h2>
          <p>Inspect macro, financial, and trade indicators for the active country.</p>
        </div>
        <select
          className={styles.select}
          value={selectedCountryId ?? ""}
          onChange={(event) => setSelectedCountry(event.target.value)}
        >
          {countries.map((country) => (
            <option key={country.id} value={country.id}>
              {country.state.name}
            </option>
          ))}
        </select>
      </header>
      {selectedCountry ? (
        <div className="grid-columns-2">
          {metrics.map((metric) => (
            <div key={metric.label} className={styles.metricCard}>
              <span className={styles.metricLabel}>{metric.label}</span>
              <span className={styles.metricValue}>{metric.value}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className={styles.empty}>Select a country to view detail.</p>
      )}
    </section>
  );
}
