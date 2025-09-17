import type {
  GlobalState,
  ScenarioDetail,
  ScenarioSummary,
  SimulationStep,
  StepAudit,
} from "@/types/simulation";

const auditFactory = (timestep: number, reducerSequence: string[]): StepAudit => ({
  scenario_id: "scenario-1",
  timestep,
  step_start_time: new Date(Date.UTC(2026, 3, 10, 12, 0, 0)).toISOString(),
  step_end_time: new Date(Date.UTC(2026, 3, 10, 12, 0, 15)).toISOString(),
  reducer_sequence: reducerSequence,
  field_changes: [
    {
      field_path: "countries.United States.macro.policy_rate",
      old_value: 0.0225,
      new_value: 0.0275,
      reducer_name: "taylor_rule",
      reducer_params: { phi_pi: 1.4, phi_y: 0.3 },
      calculation_details: { output_gap: -0.015 },
    },
  ],
  triggers_fired: timestep === 3 ? ["usd_liquidity_support"] : [],
  errors: [],
});

const baseState: GlobalState = {
  t: 2,
  base_ccy: "USD",
  countries: {
    "United States": {
      name: "United States",
      iso_a3: "USA",
      macro: {
        gdp: 23.5,
        potential_gdp: 24.1,
        inflation: 0.032,
        unemployment: 0.045,
        policy_rate: 0.0275,
        inflation_target: 0.02,
      },
      external: {
        fx_rate: 1.0,
        reserves_usd: 130.5,
        current_account_gdp: -0.018,
      },
      finance: {
        sovereign_yield: 0.031,
        credit_spread: 0.008,
        bank_tier1_ratio: 0.122,
      },
      trade: {
        exports_gdp: 0.11,
        imports_gdp: 0.135,
        tariff_mfn_avg: 0.035,
        ntm_index: 0.42,
        terms_of_trade: 1.04,
      },
      energy: {
        energy_stock_to_use: 0.64,
        energy_price_index: 112,
      },
      security: {
        milex_gdp: 0.034,
        personnel: 1400,
        conflict_intensity: 0.12,
      },
      sentiment: {
        gdelt_tone: 1.2,
        trends_salience: 0.64,
        policy_pressure: 0.42,
        approval: 0.51,
      },
    },
    China: {
      name: "China",
      iso_a3: "CHN",
      macro: {
        gdp: 17.8,
        potential_gdp: 18.6,
        inflation: 0.026,
        unemployment: 0.047,
        policy_rate: 0.023,
        inflation_target: 0.03,
      },
      external: {
        fx_rate: 7.1,
        reserves_usd: 3200,
        current_account_gdp: 0.014,
      },
      finance: {
        sovereign_yield: 0.029,
        credit_spread: 0.006,
        bank_tier1_ratio: 0.116,
      },
      trade: {
        exports_gdp: 0.19,
        imports_gdp: 0.165,
        tariff_mfn_avg: 0.045,
        ntm_index: 0.5,
        terms_of_trade: 0.97,
      },
      energy: {
        energy_stock_to_use: 0.52,
        energy_price_index: 118,
      },
      security: {
        milex_gdp: 0.019,
        personnel: 2050,
        conflict_intensity: 0.1,
      },
      sentiment: {
        gdelt_tone: -0.2,
        trends_salience: 0.49,
        policy_pressure: 0.56,
        approval: 0.44,
      },
    },
    Germany: {
      name: "Germany",
      iso_a3: "DEU",
      macro: {
        gdp: 4.4,
        potential_gdp: 4.6,
        inflation: 0.029,
        unemployment: 0.042,
        policy_rate: 0.022,
        inflation_target: 0.02,
      },
      external: {
        fx_rate: 0.94,
        reserves_usd: 90,
        current_account_gdp: 0.065,
      },
      finance: {
        sovereign_yield: 0.017,
        credit_spread: 0.004,
        bank_tier1_ratio: 0.146,
      },
      trade: {
        exports_gdp: 0.41,
        imports_gdp: 0.37,
        tariff_mfn_avg: 0.025,
        ntm_index: 0.36,
        terms_of_trade: 1.02,
      },
      energy: {
        energy_stock_to_use: 0.58,
        energy_price_index: 109,
      },
      security: {
        milex_gdp: 0.015,
        personnel: 183,
        conflict_intensity: 0.05,
      },
      sentiment: {
        gdelt_tone: 0.85,
        trends_salience: 0.57,
        policy_pressure: 0.38,
        approval: 0.49,
      },
    },
  },
  trade_matrix: {
    "United States": {
      China: 0.33,
      Germany: 0.22,
    },
    China: {
      "United States": 0.26,
      Germany: 0.17,
    },
    Germany: {
      "United States": 0.28,
      China: 0.23,
    },
  },
  interbank_matrix: {
    "United States": {
      China: 0.18,
      Germany: 0.12,
    },
    China: {
      "United States": 0.15,
      Germany: 0.09,
    },
    Germany: {
      "United States": 0.22,
      China: 0.14,
    },
  },
  alliance_graph: {
    "United States": {
      Germany: 0.9,
    },
    Germany: {
      "United States": 0.9,
    },
    China: {
      "United States": 0.2,
    },
  },
  sanctions: {
    "United States": {
      China: 0.4,
    },
    China: {
      "United States": 0.45,
    },
    Germany: {
      China: 0.25,
    },
  },
  io_coefficients: {
    manufacturing: {
      "United States": 0.24,
      China: 0.28,
      Germany: 0.19,
    },
    energy: {
      "United States": 0.18,
      China: 0.31,
      Germany: 0.22,
    },
  },
  commodity_prices: {
    oil: 86,
    gas: 14,
    wheat: 204,
  },
  rules: {
    regimes: {
      monetary: { rule: "taylor", phi_pi: 1.4, phi_y: 0.3 },
      fx: { uip_rho_base: 0.15 },
      fiscal: { wealth_tax_rate: 0.012 },
      trade: { tariff_multiplier: 1.05 },
      security: { mobilization_intensity: 0.12 },
      labor: { national_service_pct: 0.03 },
      sentiment: { propaganda_gain: 0.08 },
    },
    rng_seed: 42,
    invariants: {
      bmp6: true,
      sfc_light: true,
    },
  },
  events: {
    pending: [
      {
        id: "evt-queue-1",
        type: "disruption",
        description: "Port congestion expected in Shanghai",
        eta: "2026-05-12",
      },
    ],
    processed: [
      {
        id: "evt-processed-1",
        type: "sanction",
        description: "Secondary sanctions tightened on critical tech",
        applied_at: "2026-04-02",
      },
    ],
  },
};

const stateAtTurn = (timestep: number): GlobalState => ({
  ...baseState,
  t: timestep,
  countries: {
    ...baseState.countries,
    "United States": {
      ...baseState.countries["United States"],
      macro: {
        ...baseState.countries["United States"].macro,
        inflation:
          timestep > 2
            ? 0.034
            : baseState.countries["United States"].macro.inflation,
        policy_rate:
          timestep > 2 ? 0.0285 : baseState.countries["United States"].macro.policy_rate,
      },
    },
  },
});

const steps: SimulationStep[] = [
  {
    id: "step-1",
    scenario_id: "scenario-1",
    timestep: 1,
    state: stateAtTurn(1),
    audit: auditFactory(1, ["trade_balance", "capital_flows"]),
    created_at: new Date(Date.UTC(2026, 3, 9, 12, 0, 0)).toISOString(),
  },
  {
    id: "step-2",
    scenario_id: "scenario-1",
    timestep: 2,
    state: stateAtTurn(2),
    audit: auditFactory(2, ["monetary_policy", "fx_adjustment"]),
    created_at: new Date(Date.UTC(2026, 3, 10, 12, 0, 0)).toISOString(),
  },
  {
    id: "step-3",
    scenario_id: "scenario-1",
    timestep: 3,
    state: stateAtTurn(3),
    audit: auditFactory(3, ["monetary_policy", "liquidity_support"]),
    created_at: new Date(Date.UTC(2026, 3, 11, 12, 0, 0)).toISOString(),
  },
];

export const mockScenarioDetails: Record<string, ScenarioDetail> = {
  "scenario-1": {
    id: "scenario-1",
    name: "USD Liquidity Stress Test",
    description: "Assess contagion under accelerated sanction regime and energy shock.",
    user_id: "user-1",
    current_timestep: 3,
    created_at: new Date(Date.UTC(2026, 2, 28, 15, 0, 0)).toISOString(),
    updated_at: new Date(Date.UTC(2026, 3, 11, 12, 0, 0)).toISOString(),
    triggers_count: 4,
    current_state: stateAtTurn(3),
    history: steps,
  },
  "scenario-2": {
    id: "scenario-2",
    name: "Energy Supply Corridor",
    description: "Model Eastern Europe supply disruptions and coordinated fiscal offsets.",
    user_id: "user-1",
    current_timestep: 1,
    created_at: new Date(Date.UTC(2026, 2, 12, 10, 0, 0)).toISOString(),
    updated_at: new Date(Date.UTC(2026, 2, 20, 9, 0, 0)).toISOString(),
    triggers_count: 3,
    current_state: {
      ...stateAtTurn(1),
      t: 1,
      commodity_prices: {
        oil: 102,
        gas: 24,
        wheat: 198,
      },
      events: {
        pending: [
          {
            id: "evt-energy-1",
            type: "pipeline",
            description: "Transit fees raised for Baltic corridor",
            eta: "2026-05-02",
          },
        ],
        processed: [],
      },
    },
    history: [
      {
        id: "scenario-2-step-1",
        scenario_id: "scenario-2",
        timestep: 1,
        state: stateAtTurn(1),
        audit: auditFactory(1, ["energy_supply", "sentiment_shift"]),
        created_at: new Date(Date.UTC(2026, 2, 20, 9, 0, 0)).toISOString(),
      },
    ],
  },
};

export const mockScenarioSummaries: ScenarioSummary[] = Object.values(
  mockScenarioDetails
).map(({ history, current_state, ...summary }) => ({
  ...summary,
}));
