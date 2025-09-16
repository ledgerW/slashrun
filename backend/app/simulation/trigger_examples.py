"""Example trigger configurations for common policy scenarios."""

from typing import Dict
from db.models.state import (
    Trigger, TriggerCondition, TriggerAction,
    PolicyPatch, ReducerOverride, NetworkRewrite, EventInject
)


def load_trigger_examples() -> Dict[str, Trigger]:
    """Load example trigger configurations."""
    examples = {}
    
    # US Tariff Shock
    examples["us_tariff_shock"] = Trigger(
        name="us_tariff_shock",
        description="Implement US tariff increases on Chinese goods",
        condition=TriggerCondition(
            when="date>=2026-01-01",
            once=True
        ),
        action=TriggerAction(
            patches=[
                PolicyPatch(
                    path="rules.regimes.trade.tariff_multiplier",
                    op="set",
                    value=2.0  # Double tariff rates
                )
            ]
        ),
        expires_after_turns=12  # Expire after 3 years (12 quarters)
    )
    
    # Wealth Tax Implementation
    examples["wealth_tax"] = Trigger(
        name="wealth_tax",
        description="Implement progressive wealth tax",
        condition=TriggerCondition(
            when="country('USA').macro.debt_gdp>1.0",  # When debt > 100% of GDP
            once=True
        ),
        action=TriggerAction(
            patches=[
                PolicyPatch(
                    path="rules.regimes.fiscal.wealth_tax_rate",
                    op="set",
                    value=0.02  # 2% wealth tax
                )
            ]
        )
    )
    
    # National Service Program
    examples["national_service"] = Trigger(
        name="national_service",
        description="Implement mandatory national service",
        condition=TriggerCondition(
            when="country('USA').macro.unemployment>0.08",  # When unemployment > 8%
            once=True
        ),
        action=TriggerAction(
            patches=[
                PolicyPatch(
                    path="rules.regimes.labor.national_service_pct",
                    op="set",
                    value=5.0  # 5% of population in national service
                )
            ]
        ),
        expires_after_turns=8  # 2-year program
    )
    
    # Conflict Escalation
    examples["conflict_escalation"] = Trigger(
        name="conflict_escalation",
        description="Military mobilization in response to conflict",
        condition=TriggerCondition(
            when="country('USA').security.conflict_intensity>0.5",
            once=False  # Can trigger multiple times
        ),
        action=TriggerAction(
            patches=[
                PolicyPatch(
                    path="rules.regimes.security.mobilization_intensity",
                    op="add",
                    value=0.5  # Increase mobilization
                )
            ],
            events=[
                EventInject(
                    kind="mobilization",
                    payload={
                        "country": "USA",
                        "intensity": 0.5,
                        "reason": "conflict_response"
                    }
                )
            ]
        )
    )
    
    # Monetary Policy Regime Switch
    examples["switch_to_fx_peg"] = Trigger(
        name="switch_to_fx_peg",
        description="Switch from Taylor rule to FX peg during crisis",
        condition=TriggerCondition(
            when="country('USA').external.fx_rate>1.5",  # Large depreciation
            once=True
        ),
        action=TriggerAction(
            overrides=[
                ReducerOverride(
                    target="monetary_policy",
                    impl_name="fx_peg"
                )
            ],
            patches=[
                PolicyPatch(
                    path="rules.regimes.monetary.peg_target",
                    op="set",
                    value=1.0
                ),
                PolicyPatch(
                    path="rules.regimes.monetary.peg_strength",
                    op="set",
                    value=3.0
                )
            ]
        ),
        expires_after_turns=4  # Temporary peg for 1 year
    )
    
    # Trade War Network Effects
    examples["trade_war_sanctions"] = Trigger(
        name="trade_war_sanctions",
        description="Implement trade sanctions and alliance shifts",
        condition=TriggerCondition(
            when="rules.regimes.trade.tariff_multiplier>1.5",  # After tariffs implemented
            once=True
        ),
        action=TriggerAction(
            network_rewrites=[
                NetworkRewrite(
                    layer="trade",
                    edits=[
                        ("USA", "CHN", 0.5),  # Reduce US-China trade
                        ("CHN", "USA", 0.5)
                    ]
                ),
                NetworkRewrite(
                    layer="sanctions",
                    edits=[
                        ("USA", "CHN", 0.3),  # Moderate sanctions
                        ("CHN", "USA", 0.3)
                    ]
                )
            ]
        )
    )
    
    return examples
