export interface Macro {
  gdp?: number | null;
  potential_gdp?: number | null;
  inflation?: number | null;
  unemployment?: number | null;
  output_gap?: number | null;
  primary_balance?: number | null;
  debt_gdp?: number | null;
  neutral_rate?: number | null;
  policy_rate?: number | null;
  inflation_target?: number;
  sfa?: number;
}

export interface External {
  fx_rate?: number | null;
  reserves_usd?: number | null;
  current_account_gdp?: number | null;
  net_errors_omissions_gdp?: number;
}

export interface Finance {
  sovereign_yield?: number | null;
  credit_spread?: number | null;
  bank_tier1_ratio?: number | null;
  leverage_target?: number;
}

export interface Trade {
  exports_gdp?: number | null;
  imports_gdp?: number | null;
  tariff_mfn_avg?: number | null;
  ntm_index?: number | null;
  terms_of_trade?: number;
}

export interface EnergyFood {
  energy_stock_to_use?: number | null;
  food_price_index?: number | null;
  energy_price_index?: number | null;
}

export interface Security {
  milex_gdp?: number | null;
  personnel?: number | null;
  conflict_intensity?: number | null;
}

export interface Sentiment {
  gdelt_tone?: number | null;
  trends_salience?: number | null;
  policy_pressure?: number | null;
  approval?: number | null;
}

export interface CountryState {
  name: string;
  iso_a3?: string;
  macro: Macro;
  external: External;
  finance: Finance;
  trade: Trade;
  energy: EnergyFood;
  security: Security;
  sentiment: Sentiment;
}

export type Matrix = Record<string, Record<string, number>>;

export interface RegimeParams {
  monetary: Record<string, unknown>;
  fx: Record<string, unknown>;
  fiscal: Record<string, unknown>;
  trade: Record<string, unknown>;
  security: Record<string, unknown>;
  labor: Record<string, unknown>;
  sentiment: Record<string, unknown>;
}

export interface SimulationRules {
  regimes: RegimeParams;
  rng_seed: number;
  invariants: Record<string, boolean>;
}

export interface GlobalState {
  t: number;
  base_ccy: string;
  countries: Record<string, CountryState>;
  trade_matrix: Matrix;
  interbank_matrix: Matrix;
  alliance_graph: Matrix;
  sanctions: Matrix;
  io_coefficients: Record<string, Record<string, number>>;
  commodity_prices: Record<string, number>;
  rules: SimulationRules;
  events: Record<string, Array<Record<string, unknown>>>;
  [key: string]: unknown;
}

export interface FieldChange {
  field_path: string;
  old_value?: unknown;
  new_value?: unknown;
  reducer_name: string;
  reducer_params: Record<string, unknown>;
  calculation_details: Record<string, unknown>;
}

export interface StepAudit {
  scenario_id: string;
  timestep: number;
  step_start_time: string;
  step_end_time: string;
  reducer_sequence: string[];
  field_changes: FieldChange[];
  triggers_fired: string[];
  errors: string[];
}

export interface ScenarioSummary {
  id: string;
  name: string;
  description?: string | null;
  user_id: string;
  current_timestep: number;
  created_at: string;
  updated_at: string;
  triggers_count: number;
}

export interface SimulationStep {
  id: string;
  scenario_id: string;
  timestep: number;
  state: GlobalState;
  audit: StepAudit;
  created_at: string;
}

export interface ScenarioDetail extends ScenarioSummary {
  current_state: GlobalState;
  history: SimulationStep[];
}

export interface TriggerLog {
  fired_at_turn: number;
  trigger_name: string;
  actions_applied: Record<string, number>;
}
