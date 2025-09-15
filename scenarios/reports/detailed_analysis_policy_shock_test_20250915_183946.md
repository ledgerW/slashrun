# Scenario Analysis Report: Policy Shock Test

## Executive Summary
- **Overall Realism Score**: 0.90 (A)
- **Timesteps Completed**: 5
- **Total Field Changes**: 11
- **Triggers Fired**: 1

Excellent economic realism with consistent relationships and realistic variable ranges.

## Performance Metrics
- **Execution Time**: 0.13 seconds
- **Average Step Time**: 25.9 ms
- **Changes per Second**: 85.0

## Economic Relationships Analysis

### Taylor Rule
- **Realism Score**: 0.50
- **Description**: Central bank policy rate response to inflation and output gaps
- **Sample Size**: 4
- **Issues**: 4 identified

### Phillips Curve
- **Realism Score**: 0.92
- **Description**: Inflation response to output gaps and expectations
- **Sample Size**: 5

## Key State Evolution

### countries.USA.macro.inflation
- **Initial**: 0.0237
- **Final**: 0.0197
- **Change**: -0.0040
- **Trend**: decreasing

### countries.USA.macro.policy_rate
- **Initial**: 0.0506
- **Final**: 0.0445
- **Change**: -0.0060
- **Trend**: decreasing

### countries.USA.macro.debt_gdp
- **Initial**: 0.9500
- **Final**: 0.9500
- **Change**: 0.0000
- **Trend**: stable

## Trigger Analysis

### Emergency Rate Cut
- **First Fired**: Timestep 3
- **Fire Count**: 1
- **Associated Changes**: 2

## Key Insights

### Monetary Policy
- **Description**: Central bank policy responses observed throughout scenario
- **Realism Score**: 0.80

## Recommendations
- ✅ Reducer sequence is consistent across all timesteps
- 💡 Consider adding trade dynamics for more comprehensive economic modeling
- 💡 Consider adding exchange rate and external sector dynamics
- 🔍 Low number of field changes per step - verify all economic mechanisms are active

## Detailed Data
For complete analysis data including field-by-field changes, see the accompanying JSON file.

---
*Report generated at 2025-09-15T18:39:46.041011*
