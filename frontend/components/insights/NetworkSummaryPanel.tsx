"use client";

import { useMemo } from "react";
import { useSimulationState } from "@/lib/state/SimulationStateContext";
import styles from "./NetworkSummaryPanel.module.css";

interface NetworkRow {
  partner: string;
  weight: number;
}

function pickTop(matrix: Record<string, Record<string, number>>, key: string): NetworkRow[] {
  const row = matrix[key] ?? {};
  return Object.entries(row)
    .map(([partner, weight]) => ({ partner, weight }))
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 4);
}

export function NetworkSummaryPanel(): JSX.Element {
  const { currentState, selectedCountry, selectedCountryId, countries } = useSimulationState();

  const summary = useMemo(() => {
    if (!currentState || !selectedCountry || !selectedCountryId) {
      return null;
    }
    const keyOptions = [selectedCountryId, selectedCountry.name];
    const tradeKey = keyOptions.find((key) => currentState.trade_matrix[key]) ?? keyOptions[0];
    const interbankKey =
      keyOptions.find((key) => currentState.interbank_matrix[key]) ?? keyOptions[0];
    const allianceKey =
      keyOptions.find((key) => currentState.alliance_graph[key]) ?? keyOptions[0];
    return {
      trade: pickTop(currentState.trade_matrix, tradeKey),
      interbank: pickTop(currentState.interbank_matrix, interbankKey),
      alliance: pickTop(currentState.alliance_graph, allianceKey),
    };
  }, [currentState, selectedCountry, selectedCountryId]);

  const partnerName = useMemo(() => {
    const map = new Map(countries.map((entry) => [entry.id, entry.state.name]));
    return (partner: string) => map.get(partner) ?? partner;
  }, [countries]);

  return (
    <section className={styles.panel}>
      <header className={styles.header}>
        <h2>Network Exposures</h2>
        <p>Trade flows, interbank channels, and alliance intensity.</p>
      </header>
      {summary ? (
        <div className={styles.tableGrid}>
          <div>
            <h3>Trade</h3>
            <table className="table-compact">
              <thead>
                <tr>
                  <th>Partner</th>
                  <th>Share</th>
                </tr>
              </thead>
              <tbody>
                {summary.trade.map((row) => (
                  <tr key={`trade-${row.partner}`}>
                    <td>{partnerName(row.partner)}</td>
                    <td>{(row.weight * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div>
            <h3>Interbank</h3>
            <table className="table-compact">
              <thead>
                <tr>
                  <th>Counterparty</th>
                  <th>Weight</th>
                </tr>
              </thead>
              <tbody>
                {summary.interbank.map((row) => (
                  <tr key={`bank-${row.partner}`}>
                    <td>{partnerName(row.partner)}</td>
                    <td>{(row.weight * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div>
            <h3>Alliances</h3>
            <table className="table-compact">
              <thead>
                <tr>
                  <th>Ally</th>
                  <th>Intensity</th>
                </tr>
              </thead>
              <tbody>
                {summary.alliance.map((row) => (
                  <tr key={`alliance-${row.partner}`}>
                    <td>{partnerName(row.partner)}</td>
                    <td>{(row.weight * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <p className={styles.empty}>Select a country to inspect its network exposures.</p>
      )}
    </section>
  );
}
