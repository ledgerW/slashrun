"""Complex scenario tests combining multiple economic shocks and policy responses."""

import pytest
from httpx import AsyncClient


class TestComplexScenario:
    """Test complex multi-dimensional economic scenarios."""
    
    async def test_great_power_conflict_scenario(self, client: AsyncClient, auth_headers):
        """Test comprehensive geopolitical-economic crisis scenario."""
        
        scenario_data = {
            "name": "Great Power Conflict",
            "description": "Multi-dimensional crisis: conflict, sanctions, energy, inflation",
            "initial_state": {
                "t": 0,
                "base_ccy": "USD",
                "countries": {
                    "USA": {
                        "name": "USA",
                        "macro": {
                            "gdp": 23000000,
                            "inflation": 0.025,
                            "unemployment": 0.037,
                            "policy_rate": 0.05,
                            "debt_gdp": 0.95
                        },
                        "external": {
                            "fx_rate": 1.0,
                            "current_account_gdp": -0.025
                        },
                        "trade": {
                            "exports_gdp": 0.12,
                            "imports_gdp": 0.15,
                            "tariff_mfn_avg": 0.032
                        },
                        "energy": {
                            "energy_price_index": 100.0,
                            "energy_stock_to_use": 0.8
                        },
                        "security": {
                            "milex_gdp": 0.035,
                            "conflict_intensity": 0.0
                        }
                    },
                    "CHN": {
                        "name": "CHN",
                        "macro": {
                            "gdp": 17700000,
                            "inflation": 0.021,
                            "unemployment": 0.039,
                            "policy_rate": 0.035,
                            "debt_gdp": 0.67
                        },
                        "external": {
                            "fx_rate": 6.8,
                            "current_account_gdp": 0.015
                        },
                        "trade": {
                            "exports_gdp": 0.18,
                            "imports_gdp": 0.16,
                            "tariff_mfn_avg": 0.076
                        },
                        "security": {
                            "milex_gdp": 0.019,
                            "conflict_intensity": 0.0
                        }
                    },
                    "RUS": {
                        "name": "RUS",
                        "macro": {
                            "gdp": 1800000,
                            "inflation": 0.058,
                            "unemployment": 0.048,
                            "policy_rate": 0.065,
                            "debt_gdp": 0.17
                        },
                        "external": {
                            "fx_rate": 75.0,
                            "current_account_gdp": 0.065
                        },
                        "energy": {
                            "energy_price_index": 100.0,
                            "energy_stock_to_use": 2.5  # Major energy exporter
                        },
                        "security": {
                            "milex_gdp": 0.042,
                            "conflict_intensity": 0.0
                        }
                    },
                    "DEU": {
                        "name": "DEU",
                        "macro": {
                            "gdp": 4200000,
                            "inflation": 0.018,
                            "unemployment": 0.032,
                            "policy_rate": 0.0
                        },
                        "energy": {
                            "energy_price_index": 100.0,
                            "energy_stock_to_use": 0.15  # Energy dependent
                        }
                    }
                },
                "trade_matrix": {
                    "USA": {"CHN": 120000, "DEU": 85000, "RUS": 15000},
                    "CHN": {"USA": 450000, "DEU": 95000, "RUS": 55000},
                    "RUS": {"USA": 12000, "CHN": 48000, "DEU": 35000},
                    "DEU": {"USA": 180000, "CHN": 95000, "RUS": 25000}
                },
                "sanctions": {
                    "USA": {"RUS": 0.0},
                    "DEU": {"RUS": 0.0}
                },
                "alliance_graph": {
                    "USA": {"DEU": 0.8},
                    "DEU": {"USA": 0.8}
                },
                "commodity_prices": {
                    "oil": 80.0,
                    "gas": 6.0,
                    "wheat": 250.0
                },
                "rules": {
                    "regimes": {
                        "monetary": {"taylor_rule_enabled": True},
                        "fiscal": {"war_spending_multiplier": 2.0},
                        "security": {"conflict_escalation_rate": 0.15},
                        "trade": {"sanctions_elasticity": 0.8}
                    }
                }
            },
            "triggers": [
                {
                    "name": "Regional Conflict Erupts",
                    "description": "Major military conflict begins",
                    "condition": {"when": "t >= 2", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.RUS.security.conflict_intensity",
                                "op": "set",
                                "value": 0.7
                            },
                            {
                                "path": "countries.USA.security.milex_gdp",
                                "op": "mul",
                                "value": 1.3
                            }
                        ],
                        "events": [
                            {
                                "kind": "conflict",
                                "payload": {
                                    "intensity": 0.7,
                                    "actors": ["RUS"],
                                    "duration": 12
                                }
                            }
                        ]
                    }
                },
                {
                    "name": "Comprehensive Sanctions",
                    "description": "Western sanctions on Russian economy",
                    "condition": {"when": "t >= 3", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "sanctions.USA.RUS",
                                "op": "set",
                                "value": 0.8
                            },
                            {
                                "path": "sanctions.DEU.RUS", 
                                "op": "set",
                                "value": 0.6
                            }
                        ],
                        "network_rewrites": [
                            {
                                "layer": "trade",
                                "edits": [
                                    ["USA", "RUS", 2000],
                                    ["DEU", "RUS", 8000],
                                    ["RUS", "USA", 3000],
                                    ["RUS", "DEU", 10000]
                                ]
                            }
                        ]
                    }
                },
                {
                    "name": "Energy Weapon Response",
                    "description": "Russia weaponizes energy exports",
                    "condition": {"when": "t >= 4", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "commodity_prices.oil",
                                "op": "mul",
                                "value": 1.5
                            },
                            {
                                "path": "commodity_prices.gas",
                                "op": "mul", 
                                "value": 2.0
                            },
                            {
                                "path": "countries.DEU.energy.energy_price_index",
                                "op": "mul",
                                "value": 1.8
                            }
                        ]
                    }
                },
                {
                    "name": "Global Inflation Shock",
                    "description": "Commodity price surge drives inflation",
                    "condition": {"when": "t >= 5", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.macro.inflation",
                                "op": "add",
                                "value": 0.04
                            },
                            {
                                "path": "countries.DEU.macro.inflation",
                                "op": "add",
                                "value": 0.06
                            },
                            {
                                "path": "countries.CHN.macro.inflation",
                                "op": "add",
                                "value": 0.03
                            }
                        ]
                    }
                },
                {
                    "name": "Central Bank Emergency Response",
                    "description": "Coordinated monetary policy response",
                    "condition": {"when": "t >= 6", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.macro.policy_rate",
                                "op": "add",
                                "value": 0.025
                            },
                            {
                                "path": "countries.DEU.macro.policy_rate",
                                "op": "add",
                                "value": 0.015
                            }
                        ]
                    }
                },
                {
                    "name": "Supply Chain Realignment",
                    "description": "Countries diversify away from conflict zones",
                    "condition": {"when": "t >= 7", "once": True},
                    "action": {
                        "network_rewrites": [
                            {
                                "layer": "trade",
                                "edits": [
                                    ["USA", "CHN", 140000],  # Increase US-China trade
                                    ["CHN", "USA", 500000],
                                    ["DEU", "CHN", 110000]   # Germany increases China trade
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        # Create scenario
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Track comprehensive metrics through the crisis
        crisis_data = []
        
        for timestep in range(12):
            response = await client.post(
                f"/api/v1/simulation/scenarios/{scenario_id}/step",
                headers=auth_headers
            )
            step_data = response.json()
            
            state = step_data["state"]
            audit = step_data["audit"]
            
            crisis_data.append({
                "timestep": timestep + 1,
                "us_inflation": state["countries"]["USA"]["macro"]["inflation"],
                "deu_inflation": state["countries"]["DEU"]["macro"]["inflation"],
                "rus_conflict": state["countries"]["RUS"]["security"]["conflict_intensity"],
                "oil_price": state["commodity_prices"]["oil"],
                "gas_price": state["commodity_prices"]["gas"],
                "us_rus_sanctions": state["sanctions"]["USA"]["RUS"],
                "trade_us_rus": state["trade_matrix"]["USA"]["RUS"],
                "us_policy_rate": state["countries"]["USA"]["macro"]["policy_rate"],
                "triggers": audit["triggers_fired"],
                "field_changes": len(audit["field_changes"])
            })
        
        # Verify crisis progression
        conflict_start = next((d for d in crisis_data if "Regional Conflict Erupts" in d["triggers"]), None)
        sanctions_start = next((d for d in crisis_data if "Comprehensive Sanctions" in d["triggers"]), None)
        energy_weapon = next((d for d in crisis_data if "Energy Weapon Response" in d["triggers"]), None)
        inflation_shock = next((d for d in crisis_data if "Global Inflation Shock" in d["triggers"]), None)
        cb_response = next((d for d in crisis_data if "Central Bank Emergency Response" in d["triggers"]), None)
        
        assert all([conflict_start, sanctions_start, energy_weapon, inflation_shock, cb_response])
        
        # Verify conflict escalation
        assert conflict_start["rus_conflict"] == 0.7
        
        # Verify sanctions implementation
        assert sanctions_start["us_rus_sanctions"] == 0.8
        
        # Verify energy price shock
        initial_oil = crisis_data[0]["oil_price"]
        post_energy_oil = energy_weapon["oil_price"]
        assert post_energy_oil >= initial_oil * 1.4  # At least 40% increase
        
        # Verify inflation transmission
        initial_us_inflation = crisis_data[0]["us_inflation"]
        final_us_inflation = crisis_data[-1]["us_inflation"]
        assert final_us_inflation > initial_us_inflation + 0.035  # Significant inflation increase
        
        # Verify monetary policy response
        initial_us_rate = crisis_data[0]["us_policy_rate"]
        final_us_rate = crisis_data[-1]["us_policy_rate"]
        assert final_us_rate > initial_us_rate + 0.02  # Central bank tightening
        
        # Verify trade disruption
        initial_trade = crisis_data[0]["trade_us_rus"]
        sanctions_trade = sanctions_start["trade_us_rus"]
        assert sanctions_trade < initial_trade * 0.5  # Major trade reduction
        
        # Verify audit trail completeness
        total_changes = sum(d["field_changes"] for d in crisis_data)
        assert total_changes > 200  # Extensive economic changes tracked
        
        # Verify system stability (no crashes despite complexity)
        assert len(crisis_data) == 12  # All timesteps completed
        assert all(d["timestep"] == i + 1 for i, d in enumerate(crisis_data))
    
    async def test_financial_crisis_cascade(self, client: AsyncClient, auth_headers):
        """Test systemic financial crisis with international spillovers."""
        
        scenario_data = {
            "name": "Global Financial Crisis",
            "description": "Banking crisis, credit crunch, policy coordination",
            "initial_state": {
                "t": 0,
                "base_ccy": "USD",
                "countries": {
                    "USA": {
                        "name": "USA",
                        "macro": {
                            "gdp": 23000000,
                            "inflation": 0.025,
                            "unemployment": 0.037,
                            "policy_rate": 0.05,
                            "debt_gdp": 0.95
                        },
                        "finance": {
                            "sovereign_yield": 0.025,
                            "credit_spread": 0.015,
                            "bank_tier1_ratio": 0.13
                        },
                        "external": {
                            "fx_rate": 1.0
                        }
                    },
                    "GBR": {
                        "name": "GBR",
                        "macro": {
                            "gdp": 3100000,
                            "inflation": 0.022,
                            "unemployment": 0.035,
                            "policy_rate": 0.045,
                            "debt_gdp": 0.85
                        },
                        "finance": {
                            "sovereign_yield": 0.032,
                            "credit_spread": 0.018,
                            "bank_tier1_ratio": 0.12
                        },
                        "external": {
                            "fx_rate": 0.75
                        }
                    },
                    "EUR": {
                        "name": "EUR",
                        "macro": {
                            "gdp": 15000000,
                            "inflation": 0.019,
                            "unemployment": 0.068,
                            "policy_rate": 0.0,
                            "debt_gdp": 0.88
                        },
                        "finance": {
                            "sovereign_yield": 0.015,
                            "credit_spread": 0.022,
                            "bank_tier1_ratio": 0.14
                        }
                    }
                },
                "interbank_matrix": {
                    "USA": {"GBR": 500000, "EUR": 800000},
                    "GBR": {"USA": 450000, "EUR": 350000},
                    "EUR": {"USA": 700000, "GBR": 400000}
                },
                "rules": {
                    "regimes": {
                        "monetary": {"taylor_rule_enabled": True, "zirp_threshold": 0.005},
                        "fiscal": {"automatic_stabilizers": True},
                        "finance": {"crisis_threshold": 0.08, "bailout_probability": 0.7}
                    }
                }
            },
            "triggers": [
                {
                    "name": "Banking Sector Stress",
                    "description": "Major bank failures trigger credit crunch",
                    "condition": {"when": "t >= 2", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.finance.bank_tier1_ratio",
                                "op": "mul",
                                "value": 0.7
                            },
                            {
                                "path": "countries.USA.finance.credit_spread",
                                "op": "mul",
                                "value": 3.0
                            }
                        ]
                    }
                },
                {
                    "name": "Contagion to UK",
                    "description": "Crisis spreads through interbank linkages",
                    "condition": {"when": "t >= 3", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.GBR.finance.credit_spread",
                                "op": "mul",
                                "value": 2.5
                            },
                            {
                                "path": "countries.GBR.external.fx_rate",
                                "op": "mul",
                                "value": 1.15  # GBP weakens
                            }
                        ],
                        "network_rewrites": [
                            {
                                "layer": "interbank",
                                "edits": [
                                    ["USA", "GBR", 250000],  # Reduced interbank lending
                                    ["GBR", "USA", 200000]
                                ]
                            }
                        ]
                    }
                },
                {
                    "name": "Emergency Rate Cuts",
                    "description": "Central banks cut rates to zero",
                    "condition": {"when": "t >= 4", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.macro.policy_rate",
                                "op": "set",
                                "value": 0.0
                            },
                            {
                                "path": "countries.GBR.macro.policy_rate", 
                                "op": "set",
                                "value": 0.0
                            }
                        ]
                    }
                },
                {
                    "name": "Fiscal Stimulus Package",
                    "description": "Coordinated fiscal expansion",
                    "condition": {"when": "t >= 5", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.macro.debt_gdp",
                                "op": "add",
                                "value": 0.10  # 10pp of GDP fiscal expansion
                            },
                            {
                                "path": "countries.GBR.macro.debt_gdp",
                                "op": "add",
                                "value": 0.08
                            }
                        ]
                    }
                },
                {
                    "name": "Recovery Signs",
                    "description": "Credit markets begin to normalize",
                    "condition": {"when": "t >= 8", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.finance.credit_spread",
                                "op": "mul",
                                "value": 0.6  # Spreads compress
                            },
                            {
                                "path": "countries.GBR.finance.credit_spread",
                                "op": "mul", 
                                "value": 0.7
                            }
                        ]
                    }
                }
            ]
        }
        
        # Create scenario and track financial metrics
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        scenario_id = response.json()["id"]
        
        financial_data = []
        
        for timestep in range(10):
            response = await client.post(
                f"/api/v1/simulation/scenarios/{scenario_id}/step",
                headers=auth_headers
            )
            step_data = response.json()
            
            state = step_data["state"]
            
            financial_data.append({
                "timestep": timestep + 1,
                "us_credit_spread": state["countries"]["USA"]["finance"]["credit_spread"],
                "gbr_credit_spread": state["countries"]["GBR"]["finance"]["credit_spread"],
                "us_policy_rate": state["countries"]["USA"]["macro"]["policy_rate"],
                "gbr_policy_rate": state["countries"]["GBR"]["macro"]["policy_rate"],
                "us_debt_gdp": state["countries"]["USA"]["macro"]["debt_gdp"],
                "interbank_usa_gbr": state["interbank_matrix"]["USA"]["GBR"],
                "triggers": step_data["audit"]["triggers_fired"]
            })
        
        # Verify financial crisis sequence
        banking_stress = next((d for d in financial_data if "Banking Sector Stress" in d["triggers"]), None)
        contagion = next((d for d in financial_data if "Contagion to UK" in d["triggers"]), None)
        rate_cuts = next((d for d in financial_data if "Emergency Rate Cuts" in d["triggers"]), None)
        fiscal_stimulus = next((d for d in financial_data if "Fiscal Stimulus Package" in d["triggers"]), None)
        recovery = next((d for d in financial_data if "Recovery Signs" in d["triggers"]), None)
        
        assert all([banking_stress, contagion, rate_cuts, fiscal_stimulus, recovery])
        
        # Verify crisis impact
        initial_spread = financial_data[0]["us_credit_spread"]
        peak_spread = max(d["us_credit_spread"] for d in financial_data[:6])
        assert peak_spread > initial_spread * 2.5  # Credit spreads widen significantly
        
        # Verify policy response
        assert rate_cuts["us_policy_rate"] == 0.0
        assert rate_cuts["gbr_policy_rate"] == 0.0
        
        # Verify fiscal expansion
        initial_debt = financial_data[0]["us_debt_gdp"]
        post_stimulus_debt = fiscal_stimulus["us_debt_gdp"]
        assert post_stimulus_debt > initial_debt + 0.09  # Significant fiscal expansion
        
        # Verify recovery
        final_spread = financial_data[-1]["us_credit_spread"]
        assert final_spread < peak_spread * 0.7  # Spreads compress in recovery
