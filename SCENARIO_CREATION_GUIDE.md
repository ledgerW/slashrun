# SlashRun Scenario Creation Guide

This guide provides comprehensive documentation for creating economic simulation scenarios in SlashRun, covering all possible inputs and options for both states and triggers.

## Table of Contents

1. [Overview](#overview)
2. [Global State Structure](#global-state-structure)
3. [Country State Components](#country-state-components)
4. [Network Structures](#network-structures)
5. [Rules and Regimes](#rules-and-regimes)
6. [Trigger System](#trigger-system)
7. [Template Generation](#template-generation)
8. [Example Scenarios](#example-scenarios)

## Overview

SlashRun scenarios consist of:
- **Initial Global State**: The starting economic conditions across all countries
- **Triggers**: Policy interventions and regime switches that activate during simulation
- **Rules**: Behavioral parameters governing how the simulation evolves

## Global State Structure

The top-level GlobalState contains the following fields:

```json
{
  "t": 0,                    // Current timestep (integer)
  "base_ccy": "USD",         // Base currency (string)
  "countries": {...},        // Country-specific data (object)
  "trade_matrix": {...},     // Trade relationships (object)
  "interbank_matrix": {...}, // Financial linkages (object)  
  "alliance_graph": {...},   // Political alliances (object)
  "sanctions": {...},        // Economic sanctions (object)
  "io_coefficients": {...},  // Input-output relationships (object)
  "commodity_prices": {...}, // Global commodity prices (object)
  "rules": {...},            // Simulation rules and regimes (object)
  "events": {...}            // Event queue (object)
}
```

## Country State Components

Each country in the `countries` object has the following structure:

### Macroeconomic Data (`macro`)
```json
{
  "gdp": 27720709000000.0,           // Nominal GDP (float)
  "potential_gdp": 26334673550000.0, // Potential GDP (float)
  "inflation": 0.041,                // Inflation rate (float)
  "unemployment": 0.036,             // Unemployment rate (float)
  "output_gap": 0.053,               // Output gap (float)
  "primary_balance": 0.0,            // Primary fiscal balance/GDP (float)
  "debt_gdp": 1.148,                 // Government debt/GDP ratio (float)
  "neutral_rate": 0.02,              // Neutral interest rate (float)
  "policy_rate": 0.03,               // Central bank policy rate (float)
  "inflation_target": 0.02,          // Inflation target (float)
  "sfa": 0.0                         // Stock-flow adjustment (float)
}
```

### External Sector (`external`)
```json
{
  "fx_rate": 1.0,                    // Exchange rate vs base currency (float)
  "reserves_usd": null,              // Foreign reserves in USD (float or null)
  "current_account_gdp": 0.0,        // Current account/GDP ratio (float)
  "net_errors_omissions_gdp": 0.0    // Net errors & omissions/GDP (float)
}
```

### Financial System (`finance`)
```json
{
  "sovereign_yield": 0.035,          // 10Y government bond yield (float)
  "credit_spread": 0.01,             // Credit spread over sovereign (float)
  "bank_tier1_ratio": 0.12,          // Bank capital adequacy ratio (float)
  "leverage_target": 10.0            // Target financial leverage (float)
}
```

### Trade (`trade`)
```json
{
  "exports_gdp": 0.110,              // Exports/GDP ratio (float)
  "imports_gdp": 0.139,              // Imports/GDP ratio (float)
  "tariff_mfn_avg": 0.03,            // Average MFN tariff rate (float)
  "ntm_index": 0.35,                 // Non-tariff measures index (float)
  "terms_of_trade": 1.0              // Terms of trade index (float)
}
```

### Energy & Commodities (`energy`)
```json
{
  "energy_stock_to_use": 1.0,        // Energy stock-to-use ratio (float)
  "food_price_index": 120.0,         // Food price index (float)
  "energy_price_index": 100.0        // Energy price index (float)
}
```

### Security & Defense (`security`)
```json
{
  "milex_gdp": 0.02,                 // Military expenditure/GDP (float)
  "personnel": null,                 // Military personnel (int or null)
  "conflict_intensity": 0.0          // Current conflict intensity (float)
}
```

### Sentiment & Politics (`sentiment`)
```json
{
  "gdelt_tone": 0.0,                 // Media tone indicator (float)
  "trends_salience": 50.0,           // Search trends salience (float)
  "policy_pressure": 0.2,            // Policy pressure index (float)
  "approval": 0.55                   // Government approval rating (float)
}
```

## Network Structures

### Trade Matrix
Represents bilateral trade relationships as share of exporter's GDP:
```json
{
  "USA": {
    "CHN": 0.16,  // US exports to China = 16% of China's imports
    "MEX": 0.15,
    "CAN": 0.13
  },
  "CHN": {
    "USA": 0.18,
    "DEU": 0.08
  }
}
```

### Interbank Matrix
Financial exposures between countries (billions USD):
```json
{
  "USA": {
    "GBR": 120.0,  // US banks have $120B exposure to UK
    "JPN": 80.0
  }
}
```

### Alliance Graph
Political/military alliance strengths (0-1 scale):
```json
{
  "USA": {
    "CAN": 1.0,    // Very strong alliance
    "GBR": 1.0,
    "DEU": 0.8     // Strong but not complete alignment
  }
}
```

### Sanctions
Economic sanctions intensity (0-1 scale):
```json
{
  "USA": {
    "RUS": 0.9,    // Very strong sanctions
    "IRN": 0.8
  }
}
```

## Rules and Regimes

The `rules` object defines behavioral parameters:

```json
{
  "regimes": {
    "monetary": {
      "rule": "taylor",              // Monetary policy rule
      "phi_pi": 0.5,                // Inflation response coefficient
      "phi_y": 0.5                  // Output gap response coefficient
    },
    "fx": {
      "uip_rho_base": 0.0           // UIP deviation parameter
    },
    "fiscal": {
      "wealth_tax_rate": 0.0,       // Wealth tax rate
      "elasticity_saving": -0.3     // Saving elasticity
    },
    "trade": {
      "tariff_multiplier": 1.0,     // Tariff rate multiplier
      "ntm_shock": 0.0              // NTM shock parameter
    },
    "security": {
      "mobilization_intensity": 0.0 // Military mobilization level
    },
    "labor": {
      "national_service_pct": 0.0   // National service participation
    },
    "sentiment": {
      "propaganda_gain": 0.0        // Propaganda effectiveness
    }
  },
  "rng_seed": 42,                   // Random number seed
  "invariants": {
    "bmp6": true,                   // Use BMP6 accounting standard
    "sfc_light": true               // Use simplified SFC model
  }
}
```

### Available Monetary Policy Rules
- `"taylor"`: Standard Taylor rule
- `"fx_peg"`: Fixed exchange rate targeting
- `"inflation_targeting"`: Pure inflation targeting
- `"nominal_gdp_targeting"`: NGDP level targeting

## Trigger System

Triggers allow dynamic policy changes during simulation. Each trigger has:

### Trigger Structure
```json
{
  "name": "trigger_name",
  "description": "Human-readable description",
  "condition": {
    "when": "condition_expression",   // When to fire (string)
    "once": true                      // Fire only once (boolean)
  },
  "action": {
    "patches": [...],                 // Policy parameter changes
    "overrides": [...],               // Reducer implementation switches
    "network_rewrites": [...],        // Network topology changes
    "events": [...]                   // Event injections
  },
  "expires_after_turns": 12           // Expiry (integer or null)
}
```

### Condition Expressions
Supported syntax in `condition.when`:

```javascript
// Date comparisons (converted to timestep)
"date>=2026-01-01"                  // Fire after Jan 1, 2026

// Country field access
"country('USA').macro.inflation>0.05"    // US inflation > 5%
"country('CHN').trade.exports_gdp<0.15"  // China exports/GDP < 15%

// Rule access
"rules.regimes.trade.tariff_multiplier>1.5"  // After tariffs increased

// Logical operators
"date>=2026-01-01 && country('USA').macro.unemployment>0.08"
"country('USA').macro.debt_gdp>1.0 || country('USA').external.fx_rate>1.5"
```

### Policy Patches
Modify parameters dynamically:
```json
{
  "path": "rules.regimes.trade.tariff_multiplier",
  "op": "set",      // Operations: "set", "add", "mul"
  "value": 2.0
}
```

Common patch paths:
- `"rules.regimes.monetary.phi_pi"` - Taylor rule inflation response
- `"rules.regimes.fiscal.wealth_tax_rate"` - Wealth tax rate
- `"rules.regimes.trade.tariff_multiplier"` - Tariff multiplier
- `"rules.regimes.security.mobilization_intensity"` - Military mobilization
- `"rules.regimes.labor.national_service_pct"` - National service rate

### Reducer Overrides
Switch implementation of economic reducers:
```json
{
  "target": "monetary_policy",       // Which reducer to override
  "impl_name": "fx_peg"             // New implementation
}
```

Available overrides:
- `"monetary_policy"`: `"taylor"`, `"fx_peg"`, `"inflation_targeting"`
- `"fiscal_policy"`: `"balanced_budget"`, `"debt_stabilization"`
- `"trade_policy"`: `"free_trade"`, `"protectionist"`

### Network Rewrites
Modify network connections:
```json
{
  "layer": "trade",                  // Network layer to modify
  "edits": [                        // List of edge modifications
    {"from": "USA", "to": "CHN", "weight": 0.5}
  ]
}
```

Available layers:
- `"trade"` - Trade relationships
- `"alliances"` - Political alliances
- `"sanctions"` - Economic sanctions
- `"interbank"` - Financial linkages

### Event Injection
Add events to processing queue:
```json
{
  "kind": "mobilization",           // Event type
  "payload": {                      // Event-specific data
    "country": "USA",
    "intensity": 0.5
  }
}
```

## Template Generation

### MVS Template (Minimum Viable Scenario)
- 10 major economies
- Basic trade relationships
- Standard policy regimes
- Quarterly frequency (4 timesteps/year)

```bash
POST /api/v1/simulation/templates/mvs
```

### FIS Template (Full Information Scenario)  
- 30+ economies
- Comprehensive trade matrix
- Detailed financial networks
- Full alliance/sanctions graphs

```bash
POST /api/v1/simulation/templates/fis
```

## Example Scenarios

### 1. US-China Trade War
```json
{
  "name": "US-China Trade War",
  "description": "Escalating trade tensions between USA and China",
  "initial_state": {
    // Use MVS template as base
  },
  "triggers": [
    {
      "name": "us_tariff_shock",
      "description": "US implements tariffs on Chinese goods",
      "condition": {
        "when": "date>=2026-01-01",
        "once": true
      },
      "action": {
        "patches": [
          {
            "path": "rules.regimes.trade.tariff_multiplier",
            "op": "set",
            "value": 2.0
          }
        ],
        "network_rewrites": [
          {
            "layer": "trade",
            "edits": [
              {"from": "USA", "to": "CHN", "weight": 0.5},
              {"from": "CHN", "to": "USA", "weight": 0.5}
            ]
          }
        ]
      },
      "expires_after_turns": 12
    }
  ]
}
```

### 2. Financial Crisis Scenario
```json
{
  "name": "Global Financial Crisis",
  "description": "Banking sector stress leading to policy response",
  "triggers": [
    {
      "name": "monetary_easing",
      "condition": {
        "when": "country('USA').finance.credit_spread>0.05",
        "once": true
      },
      "action": {
        "patches": [
          {
            "path": "rules.regimes.monetary.phi_pi",
            "op": "mul",
            "value": 0.5
          }
        ]
      }
    },
    {
      "name": "fiscal_stimulus",
      "condition": {
        "when": "country('USA').macro.unemployment>0.08",
        "once": true
      },
      "action": {
        "patches": [
          {
            "path": "rules.regimes.fiscal.wealth_tax_rate",
            "op": "set",
            "value": 0.02
          }
        ]
      }
    }
  ]
}
```

### 3. Geopolitical Conflict
```json
{
  "name": "Regional Conflict Scenario",
  "description": "Military conflict affecting economic relationships",
  "triggers": [
    {
      "name": "conflict_outbreak",
      "condition": {
        "when": "date>=2026-06-01",
        "once": true
      },
      "action": {
        "patches": [
          {
            "path": "rules.regimes.security.mobilization_intensity",
            "op": "set",
            "value": 0.8
          }
        ],
        "network_rewrites": [
          {
            "layer": "sanctions",
            "edits": [
              {"from": "USA", "to": "RUS", "weight": 0.95}
            ]
          },
          {
            "layer": "alliances",
            "edits": [
              {"from": "USA", "to": "NATO", "weight": 1.0}
            ]
          }
        ],
        "events": [
          {
            "kind": "military_mobilization",
            "payload": {
              "countries": ["USA", "GBR", "FRA"],
              "intensity": 0.8
            }
          }
        ]
      }
    }
  ]
}
```

## Best Practices

### Scenario Design
1. **Start with templates**: Use MVS/FIS as foundation
2. **Gradual complexity**: Begin with simple triggers, add complexity iteratively  
3. **Realistic timing**: Use `date>=YYYY-MM-DD` for plausible trigger timing
4. **Test conditions**: Verify trigger conditions are achievable
5. **Consider interactions**: Multiple triggers can interact in complex ways

### Performance Optimization
1. **Limit triggers**: Too many triggers slow simulation
2. **Efficient conditions**: Simple conditions evaluate faster
3. **Network sparsity**: Dense networks are computationally expensive
4. **Reasonable country counts**: Start with MVS (10 countries), scale up gradually

### Validation
1. **Unit test triggers**: Verify trigger conditions and actions work as expected
2. **Audit trails**: Use audit logs to debug unexpected behavior
3. **Sensitivity analysis**: Test how robust scenarios are to parameter changes
4. **Historical calibration**: Validate against known economic episodes

## API Endpoints Summary

- `POST /api/v1/simulation/scenarios` - Create scenario
- `GET /api/v1/simulation/scenarios` - List user scenarios  
- `GET /api/v1/simulation/scenarios/{id}` - Get scenario details
- `PUT /api/v1/simulation/scenarios/{id}` - Update scenario
- `DELETE /api/v1/simulation/scenarios/{id}` - Delete scenario
- `POST /api/v1/simulation/scenarios/{id}/step` - Execute simulation step
- `GET /api/v1/simulation/scenarios/{id}/states/{timestep}` - Get state at timestep
- `POST /api/v1/simulation/templates/mvs` - Generate MVS template
- `POST /api/v1/simulation/templates/fis` - Generate FIS template
- `GET /api/v1/simulation/triggers/examples` - Get trigger examples

---

This guide provides the foundation for creating sophisticated economic simulation scenarios in SlashRun. Start with simple scenarios using templates, then gradually add complexity with triggers and custom network structures.
