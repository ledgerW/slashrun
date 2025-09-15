# Scenario Analysis Report: Global Financial Crisis

## Executive Summary
- **Overall Realism Score**: 0.90 (A)
- **Timesteps Completed**: 10
- **Total Field Changes**: 80
- **Triggers Fired**: 5

Excellent economic realism with consistent relationships and realistic variable ranges.

## Performance Metrics
- **Execution Time**: 0.53 seconds
- **Average Step Time**: 53.2 ms
- **Changes per Second**: 150.4

## Economic Relationships Analysis

### Taylor Rule
- **Realism Score**: 0.50
- **Description**: Central bank policy rate response to inflation and output gaps
- **Sample Size**: 9
- **Issues**: 9 identified

### Phillips Curve
- **Realism Score**: 0.96
- **Description**: Inflation response to output gaps and expectations
- **Sample Size**: 10

### Crisis Contagion
- **Realism Score**: 0.70
- **Description**: Transmission of financial stress between countries
- **Sample Size**: 15

## Key State Evolution

### countries.USA.macro.inflation
- **Initial**: 0.0237
- **Final**: 0.0165
- **Change**: -0.0072
- **Trend**: decreasing

### countries.USA.macro.policy_rate
- **Initial**: 0.0506
- **Final**: 0.0398
- **Change**: -0.0108
- **Trend**: decreasing

### countries.USA.macro.debt_gdp
- **Initial**: 0.9500
- **Final**: 1.0500
- **Change**: 0.1000
- **Trend**: increasing

## Trigger Analysis

### Banking Sector Stress
- **First Fired**: Timestep 2
- **Fire Count**: 1
- **Associated Changes**: 2

### Contagion to UK
- **First Fired**: Timestep 3
- **Fire Count**: 1
- **Associated Changes**: 2

### Emergency Rate Cuts
- **First Fired**: Timestep 4
- **Fire Count**: 1
- **Associated Changes**: 4

### Fiscal Stimulus Package
- **First Fired**: Timestep 5
- **Fire Count**: 1
- **Associated Changes**: 2

### Recovery Signs
- **First Fired**: Timestep 8
- **Fire Count**: 1
- **Associated Changes**: 2

## Key Insights

### Monetary Policy
- **Description**: Central bank policy responses observed throughout scenario
- **Realism Score**: 0.80

### Crisis Dynamics
- **Description**: Complex crisis evolution with multiple trigger events
- **Realism Score**: 0.90

## Recommendations
- ✅ Reducer sequence is consistent across all timesteps
- 💡 Consider adding trade dynamics for more comprehensive economic modeling

## Detailed Data
For complete analysis data including field-by-field changes, see the accompanying JSON file.

---
*Report generated at 2025-09-15T18:38:00.486457*
