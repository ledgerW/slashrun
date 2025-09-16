"""Regime-aware economic reducer functions with complete audit capture."""

import math
import random
from typing import Dict, Any, Optional, Callable, List, Set
from db.models.state import (
    GlobalState, CountryState, Macro, External, Finance, Trade, 
    EnergyFood, Security, Sentiment, RegimeParams, AuditCapture
)


# Reducer registry for implementation switching
_REDUCER_REGISTRY: Dict[str, Dict[str, Callable]] = {
    "monetary_policy": {},
    "fiscal_policy": {},
    "fx_update": {},
    "trade_update": {},
    "sentiment_update": {},
}


def register_reducer_impl(reducer_type: str, impl_name: str, impl_func: Callable) -> None:
    """Register new reducer implementation."""
    if reducer_type not in _REDUCER_REGISTRY:
        _REDUCER_REGISTRY[reducer_type] = {}
    _REDUCER_REGISTRY[reducer_type][impl_name] = impl_func


def get_reducer_impl(reducer_type: str, impl_name: Optional[str] = None) -> Callable:
    """Get reducer implementation by type and name."""
    if reducer_type not in _REDUCER_REGISTRY:
        raise ValueError(f"Unknown reducer type: {reducer_type}")
    
    impls = _REDUCER_REGISTRY[reducer_type]
    if not impls:
        raise ValueError(f"No implementations registered for reducer type: {reducer_type}")
    
    if impl_name is None:
        # Return default (first registered) implementation
        impl_name = list(impls.keys())[0]
    
    if impl_name not in impls:
        raise ValueError(f"Unknown implementation '{impl_name}' for reducer type '{reducer_type}'")
    
    return impls[impl_name]


def list_reducer_implementations(reducer_type: str) -> List[str]:
    """List available implementations for reducer type."""
    if reducer_type not in _REDUCER_REGISTRY:
        return []
    return list(_REDUCER_REGISTRY[reducer_type].keys())


# Core economic functions
def taylor_rule(m: Macro, regimes: RegimeParams, phi_pi: float = 0.5, phi_y: float = 0.5) -> float:
    """Federal Reserve Taylor rule with regime parameters."""
    # Extract regime-specific parameters
    monetary_params = regimes.monetary
    phi_pi = monetary_params.get("phi_pi", phi_pi)
    phi_y = monetary_params.get("phi_y", phi_y)
    
    # Taylor rule calculation
    if m.inflation is not None and m.output_gap is not None and m.neutral_rate is not None:
        policy_rate = (
            m.neutral_rate + 
            m.inflation + 
            phi_pi * (m.inflation - m.inflation_target) + 
            phi_y * m.output_gap
        )
        return max(0.0, policy_rate)  # Zero lower bound
    
    return m.policy_rate or 0.02  # Fallback


def monetary_policy_taylor(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None:
    """Taylor rule monetary policy implementation."""
    policy_rate_field = f"countries.{country.name}.macro.policy_rate"
    
    # Check if this field has already been modified by triggers
    if hasattr(audit, 'triggers_fired') and audit.triggers_fired:
        # Check if any trigger has modified the policy rate
        for field_change in audit.field_changes:
            if field_change.field_path == policy_rate_field:
                # Policy rate was modified by trigger, skip Taylor rule override
                audit.record_change(
                    field_path=policy_rate_field + "_taylor_rule_skipped",
                    old_value=None,
                    new_value=None,
                    calculation_details={
                        "reason": "Policy rate modified by trigger, Taylor rule skipped",
                        "trigger_set_value": country.macro.policy_rate,
                        "triggers_fired": audit.triggers_fired
                    }
                )
                return
    
    old_rate = country.macro.policy_rate or 0.02
    
    # Ensure required fields exist with defaults
    if country.macro.output_gap is None:
        country.macro.output_gap = 0.0  # Assume economy at potential
    if country.macro.neutral_rate is None:
        country.macro.neutral_rate = 0.025  # Default neutral rate
    if country.macro.inflation_target is None:
        country.macro.inflation_target = 0.02  # Default 2% target
    
    new_rate = taylor_rule(country.macro, regimes)
    
    if abs(old_rate - new_rate) > 0.0001:  # Only record meaningful changes
        audit.record_change(
            field_path=policy_rate_field,
            old_value=old_rate,
            new_value=new_rate,
            calculation_details={
                "rule": "taylor",
                "phi_pi": regimes.monetary.get("phi_pi", 0.5),
                "phi_y": regimes.monetary.get("phi_y", 0.5),
                "inflation": country.macro.inflation,
                "inflation_target": country.macro.inflation_target,
                "output_gap": country.macro.output_gap,
                "neutral_rate": country.macro.neutral_rate
            }
        )
        country.macro.policy_rate = new_rate


def monetary_policy_fx_peg(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None:
    """FX peg monetary policy implementation."""
    # Simple FX peg - maintain fixed exchange rate
    target_rate = regimes.monetary.get("peg_target", 1.0)
    old_rate = country.macro.policy_rate
    
    # Adjust policy rate to defend peg (simplified)
    if country.external.fx_rate is not None:
        fx_deviation = country.external.fx_rate - target_rate
        adjustment = regimes.monetary.get("peg_strength", 2.0) * fx_deviation
        new_rate = max(0.0, (old_rate or 0.02) + adjustment)
    else:
        new_rate = old_rate or 0.02
    
    if old_rate != new_rate:
        audit.record_change(
            field_path=f"countries.{country.name}.macro.policy_rate",
            old_value=old_rate,
            new_value=new_rate,
            calculation_details={
                "rule": "fx_peg",
                "peg_target": target_rate,
                "fx_rate": country.external.fx_rate,
                "adjustment": adjustment if 'adjustment' in locals() else 0.0
            }
        )
        country.macro.policy_rate = new_rate


# Register monetary policy implementations
register_reducer_impl("monetary_policy", "taylor", monetary_policy_taylor)
register_reducer_impl("monetary_policy", "fx_peg", monetary_policy_fx_peg)


def update_output_gap(country: CountryState, regimes: RegimeParams, audit: AuditCapture, demand_shock_pct: float = 0.0) -> None:
    """Calculate output gap changes with audit trail."""
    old_gap = country.macro.output_gap
    old_gdp = country.macro.gdp
    
    if old_gdp is not None and country.macro.potential_gdp is not None:
        # Apply demand shock
        shock_adjusted_gdp = old_gdp * (1.0 + demand_shock_pct / 100.0)
        new_gap = (shock_adjusted_gdp - country.macro.potential_gdp) / country.macro.potential_gdp
        
        audit.record_change(
            field_path=f"countries.{country.name}.macro.output_gap",
            old_value=old_gap,
            new_value=new_gap,
            calculation_details={
                "gdp": old_gdp,
                "potential_gdp": country.macro.potential_gdp,
                "demand_shock_pct": demand_shock_pct,
                "shock_adjusted_gdp": shock_adjusted_gdp
            }
        )
        country.macro.output_gap = new_gap


def update_inflation(country: CountryState, regimes: RegimeParams, audit: AuditCapture, kappa: float = 0.1, beta: float = 0.6) -> None:
    """New-Keynesian Phillips Curve inflation dynamics with audit."""
    old_inflation = country.macro.inflation
    
    if old_inflation is not None:
        # Ensure output gap exists with default
        if country.macro.output_gap is None:
            country.macro.output_gap = 0.0  # Assume economy at potential
        if country.macro.inflation_target is None:
            country.macro.inflation_target = 0.02  # Default 2% target
        
        # Phillips curve: π_t = β*E[π_{t+1}] + κ*y_t + ε_t
        expected_inflation = country.macro.inflation_target  # Simplified expectation
        supply_shock = regimes.monetary.get("supply_shock", 0.0)
        
        new_inflation = (
            beta * expected_inflation + 
            kappa * country.macro.output_gap + 
            supply_shock
        )
        
        # Add some dynamics - inflation moves gradually toward target
        adjustment_speed = 0.1
        new_inflation = old_inflation + adjustment_speed * (new_inflation - old_inflation)
        
        if abs(old_inflation - new_inflation) > 0.0001:  # Only record meaningful changes
            audit.record_change(
                field_path=f"countries.{country.name}.macro.inflation",
                old_value=old_inflation,
                new_value=new_inflation,
                calculation_details={
                    "phillips_curve": "π_t = β*E[π_{t+1}] + κ*y_t + ε_t",
                    "beta": beta,
                    "kappa": kappa,
                    "expected_inflation": expected_inflation,
                    "output_gap": country.macro.output_gap,
                    "supply_shock": supply_shock,
                    "adjustment_speed": adjustment_speed
                }
            )
            country.macro.inflation = new_inflation


def fiscal_update(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None:
    """Government finances including wealth tax and elasticities."""
    old_balance = country.macro.primary_balance
    
    # Apply wealth tax regime
    wealth_tax_rate = regimes.fiscal.get("wealth_tax_rate", 0.0)
    elasticity_saving = regimes.fiscal.get("elasticity_saving", -0.3)
    
    if country.macro.gdp is not None and old_balance is not None:
        # Wealth tax revenue as % of GDP
        wealth_tax_revenue = wealth_tax_rate * 0.1  # Simplified: 10% of GDP is taxable wealth
        
        # Behavioral response: saving rate changes
        saving_response = elasticity_saving * wealth_tax_rate
        
        new_balance = old_balance + wealth_tax_revenue + saving_response * 0.2  # 20% of GDP is private saving
        
        audit.record_change(
            field_path=f"countries.{country.name}.macro.primary_balance",
            old_value=old_balance,
            new_value=new_balance,
            calculation_details={
                "wealth_tax_rate": wealth_tax_rate,
                "wealth_tax_revenue": wealth_tax_revenue,
                "elasticity_saving": elasticity_saving,
                "saving_response": saving_response,
                "behavioral_adjustment": saving_response * 0.2
            }
        )
        country.macro.primary_balance = new_balance


def update_debt(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None:
    """IMF debt dynamics calculations with audit."""
    old_debt = country.macro.debt_gdp
    
    if (old_debt is not None and 
        country.macro.primary_balance is not None and
        country.finance.sovereign_yield is not None and
        country.macro.gdp is not None and
        country.macro.potential_gdp is not None):
        
        # Debt dynamics: d_t = d_{t-1}*(1+r)/(1+g) - pb_t + sfa_t
        real_interest_rate = country.finance.sovereign_yield - (country.macro.inflation or 0.02)
        gdp_growth = (country.macro.gdp - country.macro.potential_gdp) / country.macro.potential_gdp
        
        debt_service_ratio = (1 + real_interest_rate) / (1 + gdp_growth)
        new_debt = old_debt * debt_service_ratio - country.macro.primary_balance + country.macro.sfa
        
        audit.record_change(
            field_path=f"countries.{country.name}.macro.debt_gdp",
            old_value=old_debt,
            new_value=new_debt,
            calculation_details={
                "debt_dynamics_formula": "d_t = d_{t-1}*(1+r)/(1+g) - pb_t + sfa_t",
                "real_interest_rate": real_interest_rate,
                "gdp_growth": gdp_growth,
                "debt_service_ratio": debt_service_ratio,
                "primary_balance": country.macro.primary_balance,
                "sfa": country.macro.sfa
            }
        )
        country.macro.debt_gdp = new_debt


def settle_bop(country: CountryState, audit: AuditCapture) -> None:
    """Balance of payments identity closure with audit."""
    old_reserves = country.external.reserves_usd
    old_errors = country.external.net_errors_omissions_gdp
    
    if (country.external.current_account_gdp is not None and
        country.macro.gdp is not None):
        
        # Simplified BoP: ΔReserves = CA + Capital Account + Errors
        # For now, assume capital account balances current account
        ca_usd = country.external.current_account_gdp * country.macro.gdp
        
        # Reserve change (simplified)
        if old_reserves is not None:
            new_reserves = old_reserves + ca_usd * 0.5  # Half of CA goes to reserves
            
            audit.record_change(
                field_path=f"countries.{country.name}.external.reserves_usd",
                old_value=old_reserves,
                new_value=new_reserves,
                calculation_details={
                    "bop_identity": "ΔReserves = CA + Capital Account + Errors",
                    "current_account_usd": ca_usd,
                    "reserve_change": new_reserves - old_reserves
                }
            )
            country.external.reserves_usd = new_reserves


def update_fx(dom: CountryState, base: CountryState, regimes: RegimeParams, audit: AuditCapture, rho: float = 0.0) -> None:
    """Uncovered Interest Parity FX updates."""
    old_fx = dom.external.fx_rate
    rho = regimes.fx.get("uip_rho_base", rho)
    
    if (dom.macro.policy_rate is not None and 
        base.macro.policy_rate is not None and 
        old_fx is not None):
        
        # UIP: E[Δs] = r_domestic - r_foreign + rho
        interest_differential = dom.macro.policy_rate - base.macro.policy_rate
        expected_depreciation = interest_differential + rho
        
        # Simple FX update (log-linear approximation)
        new_fx = old_fx * (1 + expected_depreciation * 0.1)  # 10% pass-through per period
        
        audit.record_change(
            field_path=f"countries.{dom.name}.external.fx_rate",
            old_value=old_fx,
            new_value=new_fx,
            calculation_details={
                "uip_formula": "E[Δs] = r_domestic - r_foreign + rho",
                "domestic_rate": dom.macro.policy_rate,
                "foreign_rate": base.macro.policy_rate,
                "interest_differential": interest_differential,
                "risk_premium": rho,
                "expected_depreciation": expected_depreciation
            }
        )
        dom.external.fx_rate = new_fx


def trade_update(state: GlobalState, regimes: RegimeParams, audit: AuditCapture) -> None:
    """Trade flows with tariff/NTM regime parameters."""
    tariff_multiplier = regimes.trade.get("tariff_multiplier", 1.0)
    ntm_shock = regimes.trade.get("ntm_shock", 0.0)
    
    for country_name, country in state.countries.items():
        old_exports = country.trade.exports_gdp
        old_imports = country.trade.imports_gdp
        old_tariff = country.trade.tariff_mfn_avg
        
        if old_exports is not None and old_imports is not None:
            # Apply tariff regime effects
            if old_tariff is not None:
                effective_tariff = old_tariff * tariff_multiplier
                tariff_impact = -0.5 * (effective_tariff - (old_tariff or 0))  # Trade elasticity = -0.5
            else:
                tariff_impact = 0.0
            
            # Apply NTM shock
            ntm_impact = -ntm_shock * 0.3  # NTM elasticity = -0.3
            
            # Update trade flows
            trade_impact = tariff_impact + ntm_impact
            new_exports = old_exports * (1 + trade_impact)
            new_imports = old_imports * (1 + trade_impact)
            
            audit.record_change(
                field_path=f"countries.{country_name}.trade.exports_gdp",
                old_value=old_exports,
                new_value=new_exports,
                calculation_details={
                    "tariff_multiplier": tariff_multiplier,
                    "effective_tariff": effective_tariff if 'effective_tariff' in locals() else None,
                    "tariff_impact": tariff_impact,
                    "ntm_shock": ntm_shock,
                    "ntm_impact": ntm_impact,
                    "total_trade_impact": trade_impact
                }
            )
            
            audit.record_change(
                field_path=f"countries.{country_name}.trade.imports_gdp",
                old_value=old_imports,
                new_value=new_imports,
                calculation_details={
                    "tariff_multiplier": tariff_multiplier,
                    "effective_tariff": effective_tariff if 'effective_tariff' in locals() else None,
                    "tariff_impact": tariff_impact,
                    "ntm_shock": ntm_shock,
                    "ntm_impact": ntm_impact,
                    "total_trade_impact": trade_impact
                }
            )
            
            country.trade.exports_gdp = new_exports
            country.trade.imports_gdp = new_imports


def labor_supply_update(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None:
    """Labor supply effects from national service."""
    national_service_pct = regimes.labor.get("national_service_pct", 0.0)
    old_unemployment = country.macro.unemployment
    
    if old_unemployment is not None and national_service_pct > 0:
        # National service reduces effective labor supply
        labor_reduction = national_service_pct / 100.0
        unemployment_impact = -labor_reduction * 0.5  # 50% pass-through to unemployment rate
        
        new_unemployment = max(0.01, old_unemployment + unemployment_impact)  # Floor at 1%
        
        audit.record_change(
            field_path=f"countries.{country.name}.macro.unemployment",
            old_value=old_unemployment,
            new_value=new_unemployment,
            calculation_details={
                "national_service_pct": national_service_pct,
                "labor_reduction": labor_reduction,
                "unemployment_impact": unemployment_impact,
                "pass_through_rate": 0.5
            }
        )
        country.macro.unemployment = new_unemployment


def security_update(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None:
    """Military expenditure and mobilization effects."""
    mobilization_intensity = regimes.security.get("mobilization_intensity", 0.0)
    old_milex = country.security.milex_gdp
    old_personnel = country.security.personnel
    
    if mobilization_intensity > 0 and old_milex is not None:
        # Mobilization increases military spending
        mobilization_boost = mobilization_intensity * 0.02  # 2% of GDP per mobilization unit
        new_milex = old_milex + mobilization_boost
        
        audit.record_change(
            field_path=f"countries.{country.name}.security.milex_gdp",
            old_value=old_milex,
            new_value=new_milex,
            calculation_details={
                "mobilization_intensity": mobilization_intensity,
                "mobilization_boost": mobilization_boost,
                "boost_per_unit": 0.02
            }
        )
        country.security.milex_gdp = new_milex
        
        # Also increase personnel if available
        if old_personnel is not None:
            personnel_increase = int(mobilization_intensity * 10000)  # 10k per mobilization unit
            new_personnel = old_personnel + personnel_increase
            
            audit.record_change(
                field_path=f"countries.{country.name}.security.personnel",
                old_value=old_personnel,
                new_value=new_personnel,
                calculation_details={
                    "mobilization_intensity": mobilization_intensity,
                    "personnel_increase": personnel_increase,
                    "increase_per_unit": 10000
                }
            )
            country.security.personnel = new_personnel


def reduce_world(state: GlobalState, base_ccy_country: str, audit: AuditCapture) -> GlobalState:
    """Master world-level turn reducer with audit trail."""
    # Get base currency country for FX calculations
    base_country = state.countries.get(base_ccy_country)
    if not base_country:
        audit.add_error(f"Base currency country '{base_ccy_country}' not found")
        return state
    
    # Apply reducers in sequence with audit trail
    reducer_sequence = [
        "output_gap_update",
        "inflation_update", 
        "monetary_policy",
        "fiscal_update",
        "debt_update",
        "fx_update",
        "trade_update",
        "labor_supply_update",
        "security_update",
        "bop_settlement"
    ]
    
    for reducer_name in reducer_sequence:
        audit.add_reducer(reducer_name)
        
        try:
            for country_name, country in state.countries.items():
                if reducer_name == "output_gap_update":
                    update_output_gap(country, state.rules.regimes, audit)
                elif reducer_name == "inflation_update":
                    update_inflation(country, state.rules.regimes, audit)
                elif reducer_name == "monetary_policy":
                    # Use registry to get implementation
                    monetary_impl = get_reducer_impl("monetary_policy", 
                                                   state.rules.regimes.monetary.get("rule", "taylor"))
                    monetary_impl(country, state.rules.regimes, audit)
                elif reducer_name == "fiscal_update":
                    fiscal_update(country, state.rules.regimes, audit)
                elif reducer_name == "debt_update":
                    update_debt(country, state.rules.regimes, audit)
                elif reducer_name == "fx_update" and country_name != base_ccy_country:
                    update_fx(country, base_country, state.rules.regimes, audit)
                elif reducer_name == "labor_supply_update":
                    labor_supply_update(country, state.rules.regimes, audit)
                elif reducer_name == "security_update":
                    security_update(country, state.rules.regimes, audit)
                elif reducer_name == "bop_settlement":
                    settle_bop(country, audit)
            
            # Global reducers
            if reducer_name == "trade_update":
                trade_update(state, state.rules.regimes, audit)
                    
        except Exception as e:
            audit.add_error(f"Error in {reducer_name}: {str(e)}")
    
    # Increment time
    state.t += 1
    return state
