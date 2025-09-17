"use client";

import { useEffect, useMemo, useState } from "react";
import { ComposableMap, Geographies, Geography, ZoomableGroup } from "react-simple-maps";
import { feature } from "topojson-client";
import { geoMercator, geoPath } from "d3-geo";
import type { FeatureCollection, LineString } from "geojson";
import { useSimulationState } from "@/lib/state/SimulationStateContext";
import type { CountryState } from "@/types/simulation";
import styles from "./MapView.module.css";

const geoUrl = "/data/world-110m.json";

type MapFeature = FeatureCollection["features"][number];

const countryCoordinates: Record<string, [number, number]> = {
  "United States": [-98.0, 38.0],
  China: [103.0, 35.0],
  Germany: [10.5, 51.0],
  Russia: [100.0, 60.0],
  Ukraine: [31.0, 49.0],
  "United Kingdom": [-1.0, 54.0],
  France: [2.0, 46.0],
  Japan: [138.0, 37.0],
  India: [78.0, 22.0],
};

function matchCountry(
  candidates: Array<{ id: string; state: CountryState }>,
  name: string
): { id: string; state: CountryState } | undefined {
  const direct = candidates.find((entry) => entry.state.name === name || entry.id === name);
  if (direct) return direct;
  const normalizedName = name.toLowerCase();
  return candidates.find(
    (entry) =>
      entry.state.name.toLowerCase() === normalizedName || entry.id.toLowerCase() === normalizedName
  );
}

function colorForCountry(
  entry: { id: string; state: CountryState } | undefined,
  isActive: boolean
): string {
  if (!entry) {
    return "rgba(28, 40, 68, 0.7)";
  }
  const inflation = entry.state.macro.inflation ?? entry.state.macro.inflation_target ?? 0.02;
  const gap = (inflation - (entry.state.macro.inflation_target ?? 0.02)) * 120;
  const clamped = Math.max(-20, Math.min(gap, 30));
  const base = 0.6 + clamped / 100;
  if (isActive) {
    return `rgba(78, 168, 255, ${0.35 + base / 3})`;
  }
  return `rgba(44, 70, 118, ${base})`;
}

function computeLinks(
  matrix: Record<string, Record<string, number>>,
  sourceEntry: { id: string; state: CountryState } | undefined,
  candidates: Array<{ id: string; state: CountryState }>,
  threshold: number
) {
  if (!sourceEntry) return [] as Array<{ from: [number, number]; to: [number, number]; weight: number }>;
  const keyOptions = [sourceEntry.id, sourceEntry.state.name];
  const rowKey = keyOptions.find((key) => matrix[key]);
  if (!rowKey) return [];
  const row = matrix[rowKey];
  const origin = countryCoordinates[sourceEntry.state.name] ?? countryCoordinates[sourceEntry.id];
  if (!origin) return [];
  return Object.entries(row)
    .filter(([, weight]) => weight >= threshold)
    .map(([partnerKey, weight]) => {
      const partner = matchCountry(candidates, partnerKey);
      const target = partner
        ? countryCoordinates[partner.state.name] ?? countryCoordinates[partner.id]
        : undefined;
      if (!target) {
        return undefined;
      }
      return { from: origin, to: target, weight };
    })
    .filter((value): value is { from: [number, number]; to: [number, number]; weight: number } =>
      Boolean(value)
    );
}

export function MapView(): JSX.Element {
  const { currentState, countries, selectedCountryId, setSelectedCountry } = useSimulationState();
  const [features, setFeatures] = useState<MapFeature[]>([]);

  useEffect(() => {
    let cancelled = false;
    fetch(geoUrl)
      .then((response) => response.json())
      .then((data) => {
        if (cancelled) return;
        if (data.type === "Topology" && data.objects?.countries) {
          const geojson = feature(data, data.objects.countries) as FeatureCollection;
          setFeatures(geojson.features as MapFeature[]);
        } else if (data.type === "FeatureCollection") {
          setFeatures((data as FeatureCollection).features as MapFeature[]);
        }
      })
      .catch((error) => {
        console.warn("Failed to load map data", error);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const countryLookup = useMemo(() => {
    return new Map(countries.map((entry) => [entry.state.name, entry]));
  }, [countries]);

  const selectedEntry = useMemo(
    () => countries.find((entry) => entry.id === selectedCountryId),
    [countries, selectedCountryId]
  );

  const projection = useMemo(
    () => geoMercator().scale(140).center([15, 25]).translate([400, 240]),
    []
  );
  const pathGenerator = useMemo(() => geoPath(projection), [projection]);

  const tradeLinks = useMemo(
    () =>
      currentState
        ? computeLinks(currentState.trade_matrix ?? {}, selectedEntry, countries, 0.15)
        : [],
    [currentState, selectedEntry, countries]
  );

  const sanctionLinks = useMemo(
    () =>
      currentState
        ? computeLinks(currentState.sanctions ?? {}, selectedEntry, countries, 0.25)
        : [],
    [currentState, selectedEntry, countries]
  );

  const tradePaths = useMemo(() =>
    tradeLinks
      .map((link) => ({
        path: pathGenerator({
          type: "LineString",
          coordinates: [link.from, link.to],
        } as LineString),
        weight: link.weight,
      }))
      .filter((item): item is { path: string; weight: number } => Boolean(item.path)),
  [tradeLinks, pathGenerator]);

  const sanctionPaths = useMemo(() =>
    sanctionLinks
      .map((link) => ({
        path: pathGenerator({
          type: "LineString",
          coordinates: [link.from, link.to],
        } as LineString),
        weight: link.weight,
      }))
      .filter((item): item is { path: string; weight: number } => Boolean(item.path)),
  [sanctionLinks, pathGenerator]);

  return (
    <div className={styles.container}>
      <div className={styles.mapWrapper}>
        <ComposableMap projectionConfig={{ scale: 140 }}>
          <ZoomableGroup center={[15, 25]} zoom={1.05}>
            <Geographies geography={{ type: "FeatureCollection", features }}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const entry = countryLookup.get(geo.properties.name as string);
                  const isActive = selectedEntry && entry?.id === selectedEntry.id;
                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      className={styles.geography}
                      onClick={() => {
                        const matched = matchCountry(countries, geo.properties.name as string);
                        if (matched) {
                          setSelectedCountry(matched.id);
                        }
                      }}
                      style={{
                        default: {
                          fill: colorForCountry(entry, Boolean(isActive)),
                          stroke: "rgba(12,18,32,0.5)",
                          strokeWidth: 0.6,
                        },
                        hover: {
                          fill: "rgba(92, 170, 255, 0.45)",
                          stroke: "rgba(78, 168, 255, 0.7)",
                          strokeWidth: 0.9,
                        },
                        pressed: {
                          fill: "rgba(102, 184, 255, 0.55)",
                          stroke: "rgba(78, 168, 255, 0.9)",
                          strokeWidth: 1.1,
                        },
                      }}
                    />
                  );
                })
              }
            </Geographies>
            {tradePaths.map((link) => (
              <path
                key={`trade-${link.path}`}
                d={link.path}
                className={styles.tradeLink}
                style={{ opacity: Math.min(1, link.weight * 2) }}
              />
            ))}
            {sanctionPaths.map((link) => (
              <path
                key={`sanction-${link.path}`}
                d={link.path}
                className={styles.sanctionLink}
                style={{ opacity: Math.min(1, link.weight * 1.5) }}
              />
            ))}
          </ZoomableGroup>
        </ComposableMap>
      </div>
      <div className={styles.overlay}>
        <div className={styles.overlayHeader}>
          <h3>{selectedEntry?.state.name ?? "Select a country"}</h3>
          {selectedEntry ? (
            <span className="tag">{selectedEntry.id}</span>
          ) : (
            <span className="tag tag--warning">No selection</span>
          )}
        </div>
        {selectedEntry && (
          <div className={styles.overlayContent}>
            <div>
              <p>
                <span className={styles.metricLabel}>Inflation</span>
                <span className={styles.metricValue}>
                  {((selectedEntry.state.macro.inflation ?? 0) * 100).toFixed(2)}%
                </span>
              </p>
              <p>
                <span className={styles.metricLabel}>Policy rate</span>
                <span className={styles.metricValue}>
                  {((selectedEntry.state.macro.policy_rate ?? 0) * 100).toFixed(2)}%
                </span>
              </p>
            </div>
            <div>
              <p>
                <span className={styles.metricLabel}>Trade exposure</span>
                <span className={styles.metricValue}>{tradeLinks.length} routes</span>
              </p>
              <p>
                <span className={styles.metricLabel}>Sanctions</span>
                <span className={styles.metricValue}>{sanctionLinks.length} links</span>
              </p>
            </div>
          </div>
        )}
        {currentState && (
          <div className={styles.overlayFooter}>
            <div>
              <span className={styles.metricLabel}>Commodity Index</span>
              <strong>
                {Object.entries(currentState.commodity_prices)
                  .map(([commodity, price]) => `${commodity.toUpperCase()}: ${price}`)
                  .join("  |  ")}
              </strong>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
