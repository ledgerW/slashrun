"""Medium complexity scenario tests with multi-country interactions."""

import pytest
from httpx import AsyncClient


class TestMediumComplexityScenario:
    """Test medium complexity scenarios with multi-country trade and shocks."""
    
    async def test_trade_war_scenario(self, client: AsyncClient, auth_headers):
        """Test escalating trade war between USA and China."""
        
        scenario_data = {
            "name": "US-China Trade War",
            "description": "Escalating tariff war with economic impacts",
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
                        }
                    }
                },
                "trade_matrix": {
                    "USA": {"CHN": 120000},
                    "CHN": {"USA": 450000}
                },
                "rules": {
                    "regimes": {
                        "monetary": {"taylor_rule_enabled": True},
                        "trade": {"trade_elasticity": 1.2}
                    }
                }
            },
            "triggers": [
                {
                    "name": "Phase 1 Tariffs",
                    "description": "US imposes 25% tariffs on Chinese goods",
                    "condition": {"when": "t >= 2", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.trade.tariff_mfn_avg",
                                "op": "set",
                                "value": 0.25
                            }
                        ]
                    }
                },
                {
                    "name": "Chinese Retaliation",
                    "description": "China retaliates with own tariffs",
                    "condition": {"when": "t >= 4", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.CHN.trade.tariff_mfn_avg",
                                "op": "set", 
                                "value": 0.20
                            }
                        ]
                    }
                },
                {
                    "name": "Trade Volume Adjustment",
                    "description": "Reduce bilateral trade volumes",
                    "condition": {"when": "t >= 5", "once": True},
                    "action": {
                        "network_rewrites": [
                            {
                                "layer": "trade",
                                "edits": [
                                    ["USA", "CHN", 60000],  # Reduce US imports from China
                                    ["CHN", "USA", 200000]  # Reduce Chinese exports to US
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
        
        # Track key metrics through the trade war
        trade_data = []
        
        for timestep in range(8):
            response = await client.post(
                f"/api/v1/simulation/scenarios/{scenario_id}/step",
                headers=auth_headers
            )
            step_data = response.json()
            
            state = step_data["state"]
            audit = step_data["audit"]
            
            # Track trade metrics
            us_tariff = state["countries"]["USA"]["trade"]["tariff_mfn_avg"]
            cn_tariff = state["countries"]["CHN"]["trade"]["tariff_mfn_avg"]
            trade_volume_us_cn = state["trade_matrix"].get("USA", {}).get("CHN", 0)
            
            trade_data.append({
                "timestep": timestep + 1,
                "us_tariff": us_tariff,
                "cn_tariff": cn_tariff,
                "trade_volume": trade_volume_us_cn,
                "triggers_fired": audit["triggers_fired"]
            })
        
        # Verify trigger sequence
        phase1_step = next((d for d in trade_data if "Phase 1 Tariffs" in d["triggers_fired"]), None)
        retaliation_step = next((d for d in trade_data if "Chinese Retaliation" in d["triggers_fired"]), None)
        trade_adj_step = next((d for d in trade_data if "Trade Volume Adjustment" in d["triggers_fired"]), None)
        
        assert phase1_step is not None
        assert retaliation_step is not None
        assert trade_adj_step is not None
        
        # Verify tariff escalation
        assert phase1_step["us_tariff"] == 0.25
        assert retaliation_step["cn_tariff"] == 0.20
        
        # Verify trade volume reduction
        initial_trade = trade_data[0]["trade_volume"]
        final_trade = trade_data[-1]["trade_volume"] 
        assert final_trade < initial_trade
    
    async def test_currency_crisis_contagion(self, client: AsyncClient, auth_headers):
        """Test currency crisis spreading across linked economies."""
        
        scenario_data = {
            "name": "Emerging Market Currency Crisis",
            "description": "Currency crisis with regional contagion effects",
            "initial_state": {
                "t": 0,
                "base_ccy": "USD",
                "countries": {
                    "TUR": {  # Turkey - crisis epicenter
                        "name": "TUR",
                        "macro": {
                            "gdp": 760000,
                            "inflation": 0.15,  # High inflation
                            "policy_rate": 0.17,
                            "debt_gdp": 0.41
                        },
                        "external": {
                            "fx_rate": 8.5,
                            "current_account_gdp": -0.032,  # Large deficit
                            "reserves_usd": 90000
                        }
                    },
                    "BRA": {  # Brazil - susceptible to contagion
                        "name": "BRA",
                        "macro": {
                            "gdp": 2100000,
                            "inflation": 0.045,
                            "policy_rate": 0.065,
                            "debt_gdp": 0.89
                        },
                        "external": {
                            "fx_rate": 5.2,
                            "current_account_gdp": -0.013,
                            "reserves_usd": 360000
                        }
                    },
                    "USA": {  # Safe haven
                        "name": "USA",
                        "macro": {
                            "gdp": 23000000,
                            "inflation": 0.025,
                            "policy_rate": 0.05,
                            "debt_gdp": 0.95
                        },
                        "external": {
                            "fx_rate": 1.0,
                            "current_account_gdp": -0.025
                        }
                    }
                },
                "rules": {
                    "regimes": {
                        "monetary": {"taylor_rule_enabled": True},
                        "fx": {"crisis_threshold": 0.15}  # FX depreciation threshold
                    }
                }
            },
            "triggers": [
                {
                    "name": "Turkish Lira Crisis",
                    "description": "Sharp devaluation of Turkish Lira",
                    "condition": {"when": "t >= 3", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.TUR.external.fx_rate",
                                "op": "mul",
                                "value": 1.3  # 30% devaluation
                            },
                            {
                                "path": "countries.TUR.external.reserves_usd", 
                                "op": "mul",
                                "value": 0.7  # Reserve depletion
                            }
                        ]
                    }
                },
                {
                    "name": "Contagion to Brazil",
                    "description": "Market fears spread to Brazil",
                    "condition": {"when": "t >= 5", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.BRA.external.fx_rate",
                                "op": "mul",
                                "value": 1.15  # 15% devaluation
                            },
                            {
                                "path": "countries.BRA.macro.policy_rate",
                                "op": "add",
                                "value": 0.03  # Emergency rate hike
                            }
                        ]
                    }
                },
                {
                    "name": "Flight to USD",
                    "description": "Safe haven demand for USD",
                    "condition": {"when": "t >= 4", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.macro.policy_rate",
                                "op": "add",
                                "value": -0.005  # Slightly lower rate due to safe haven flows
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
        
        # Track FX and monetary policy through crisis
        crisis_data = []
        
        for timestep in range(8):
            response = await client.post(
                f"/api/v1/simulation/scenarios/{scenario_id}/step",
                headers=auth_headers
            )
            step_data = response.json()
            
            state = step_data["state"]
            
            crisis_data.append({
                "timestep": timestep + 1,
                "tur_fx": state["countries"]["TUR"]["external"]["fx_rate"],
                "bra_fx": state["countries"]["BRA"]["external"]["fx_rate"],
                "tur_reserves": state["countries"]["TUR"]["external"]["reserves_usd"],
                "bra_rate": state["countries"]["BRA"]["macro"]["policy_rate"],
                "triggers": step_data["audit"]["triggers_fired"]
            })
        
        # Find crisis events
        lira_crisis = next((d for d in crisis_data if "Turkish Lira Crisis" in d["triggers"]), None)
        contagion = next((d for d in crisis_data if "Contagion to Brazil" in d["triggers"]), None)
        
        assert lira_crisis is not None
        assert contagion is not None
        
        # Verify currency movements
        pre_crisis_tur_fx = crisis_data[1]["tur_fx"]  # t=2
        post_crisis_tur_fx = lira_crisis["tur_fx"]
        assert post_crisis_tur_fx > pre_crisis_tur_fx * 1.25  # At least 25% weaker
        
        # Verify contagion effect
        pre_contagion_bra_fx = crisis_data[3]["bra_fx"]  # t=4
        post_contagion_bra_fx = contagion["bra_fx"]
        assert post_contagion_bra_fx > pre_contagion_bra_fx  # Brazil currency also weakened
        
        # Verify policy response
        initial_bra_rate = crisis_data[0]["bra_rate"]
        final_bra_rate = crisis_data[-1]["bra_rate"]
        assert final_bra_rate > initial_bra_rate + 0.025  # Significant rate hike
    
    async def test_supply_chain_disruption(self, client: AsyncClient, auth_headers):
        """Test global supply chain disruption scenario."""
        
        scenario_data = {
            "name": "Supply Chain Shock",
            "description": "Manufacturing disruption with inflation spillovers",
            "initial_state": {
                "t": 0,
                "base_ccy": "USD", 
                "countries": {
                    "CHN": {  # Manufacturing hub
                        "name": "CHN",
                        "macro": {
                            "gdp": 17700000,
                            "inflation": 0.021,
                            "unemployment": 0.039,
                            "policy_rate": 0.035
                        },
                        "trade": {
                            "exports_gdp": 0.18,
                            "imports_gdp": 0.16
                        }
                    },
                    "USA": {  # Major importer
                        "name": "USA", 
                        "macro": {
                            "gdp": 23000000,
                            "inflation": 0.025,
                            "unemployment": 0.037,
                            "policy_rate": 0.05
                        },
                        "trade": {
                            "exports_gdp": 0.12,
                            "imports_gdp": 0.15
                        }
                    },
                    "DEU": {  # European manufacturing
                        "name": "DEU",
                        "macro": {
                            "gdp": 4200000,
                            "inflation": 0.018,
                            "unemployment": 0.032,
                            "policy_rate": 0.0
                        },
                        "trade": {
                            "exports_gdp": 0.47,
                            "imports_gdp": 0.41
                        }
                    }
                },
                "trade_matrix": {
                    "CHN": {"USA": 450000, "DEU": 120000},
                    "USA": {"CHN": 120000, "DEU": 85000},
                    "DEU": {"CHN": 95000, "USA": 180000}
                },
                "rules": {
                    "regimes": {
                        "monetary": {"taylor_rule_enabled": True},
                        "trade": {"supply_chain_sensitivity": 0.3}
                    }
                }
            },
            "triggers": [
                {
                    "name": "Chinese Factory Shutdowns",
                    "description": "Major supply disruption in China",
                    "condition": {"when": "t >= 2", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.CHN.trade.exports_gdp",
                                "op": "mul",
                                "value": 0.75  # 25% reduction in exports
                            }
                        ],
                        "network_rewrites": [
                            {
                                "layer": "trade",
                                "edits": [
                                    ["CHN", "USA", 300000],  # Reduced exports to US
                                    ["CHN", "DEU", 80000]    # Reduced exports to Germany
                                ]
                            }
                        ]
                    }
                },
                {
                    "name": "Inflation Shock USA",
                    "description": "Supply shortage drives US inflation",
                    "condition": {"when": "t >= 4", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.macro.inflation",
                                "op": "add",
                                "value": 0.03  # 3pp inflation increase
                            }
                        ]
                    }
                },
                {
                    "name": "German Manufacturing Impact",
                    "description": "German industrial production affected",
                    "condition": {"when": "t >= 3", "once": True},
                    "action": {
                        "patches": [
                            {
                                "path": "countries.DEU.macro.unemployment",
                                "op": "add",
                                "value": 0.01  # 1pp unemployment increase
                            },
                            {
                                "path": "countries.DEU.trade.exports_gdp",
                                "op": "mul", 
                                "value": 0.95  # Small reduction in exports
                            }
                        ]
                    }
                }
            ]
        }
        
        # Create scenario and run simulation
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Track supply chain metrics
        supply_data = []
        
        for timestep in range(7):
            response = await client.post(
                f"/api/v1/simulation/scenarios/{scenario_id}/step",
                headers=auth_headers
            )
            step_data = response.json()
            
            state = step_data["state"]
            
            supply_data.append({
                "timestep": timestep + 1,
                "chn_exports": state["countries"]["CHN"]["trade"]["exports_gdp"],
                "usa_inflation": state["countries"]["USA"]["macro"]["inflation"],
                "deu_unemployment": state["countries"]["DEU"]["macro"]["unemployment"],
                "trade_chn_usa": state["trade_matrix"]["CHN"]["USA"],
                "triggers": step_data["audit"]["triggers_fired"]
            })
        
        # Verify supply chain disruption sequence
        factory_shutdown = next((d for d in supply_data if "Chinese Factory Shutdowns" in d["triggers"]), None)
        inflation_shock = next((d for d in supply_data if "Inflation Shock USA" in d["triggers"]), None)
        german_impact = next((d for d in supply_data if "German Manufacturing Impact" in d["triggers"]), None)
        
        assert factory_shutdown is not None
        assert inflation_shock is not None
        assert german_impact is not None
        
        # Verify economic impacts
        initial_chn_exports = supply_data[0]["chn_exports"]
        final_chn_exports = supply_data[-1]["chn_exports"]
        assert final_chn_exports < initial_chn_exports  # Chinese exports declined
        
        initial_usa_inflation = supply_data[0]["usa_inflation"] 
        final_usa_inflation = supply_data[-1]["usa_inflation"]
        assert final_usa_inflation > initial_usa_inflation + 0.025  # Significant inflation increase
        
        # Verify trade flow changes
        initial_trade = supply_data[0]["trade_chn_usa"]
        post_disruption_trade = supply_data[-1]["trade_chn_usa"]
        assert post_disruption_trade < initial_trade  # Trade volumes reduced
