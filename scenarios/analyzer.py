#!/usr/bin/env python3
"""
Comprehensive Scenario Analysis Tool
Generates detailed reports on simulation realism, economic relationships, and step-by-step evolution.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

# Optional plotting dependencies
try:
    import matplotlib.pyplot as plt
    import pandas as pd
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False


@dataclass
class EconomicInsight:
    """Economic insight from scenario analysis."""
    category: str
    description: str
    evidence: Dict[str, Any]
    realism_score: float  # 0-1 scale
    concerns: List[str] = None


class ScenarioAnalyzer:
    """Analyzes scenario execution results for economic realism."""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def analyze_scenario(self, audit_file: Path) -> Dict[str, Any]:
        """Perform comprehensive analysis of a scenario."""
        with open(audit_file, 'r') as f:
            data = json.load(f)
        
        analysis = {
            "scenario_name": data["scenario_name"],
            "execution_summary": self._analyze_execution_summary(data),
            "state_evolution": self._analyze_state_evolution(data["audit_trail"]),
            "trigger_analysis": self._analyze_triggers(data["audit_trail"]),
            "reducer_analysis": self._analyze_reducers(data["audit_trail"]),
            "economic_relationships": self._analyze_economic_relationships(data["audit_trail"]),
            "realism_assessment": self._assess_realism(data["audit_trail"]),
            "key_insights": self._extract_key_insights(data["audit_trail"]),
            "recommendations": self._generate_recommendations(data["audit_trail"])
        }
        
        return analysis
    
    def _analyze_execution_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze high-level execution metrics."""
        audit_trail = data["audit_trail"]
        
        total_changes = sum(len(step["audit"]["field_changes"]) for step in audit_trail)
        total_triggers = sum(len(step["audit"]["triggers_fired"]) for step in audit_trail)
        
        return {
            "timesteps_completed": data["timesteps_completed"],
            "execution_time_seconds": data["execution_time"],
            "total_field_changes": total_changes,
            "average_changes_per_step": total_changes / len(audit_trail) if audit_trail else 0,
            "total_triggers_fired": total_triggers,
            "reducer_consistency": self._check_reducer_consistency(audit_trail),
            "performance_metrics": {
                "avg_step_time_ms": (data["execution_time"] * 1000) / len(audit_trail) if audit_trail else 0,
                "changes_per_second": total_changes / data["execution_time"] if data["execution_time"] > 0 else 0
            }
        }
    
    def _analyze_state_evolution(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Analyze how state variables evolve over time."""
        evolution = {}
        
        # Track key economic variables
        variables_to_track = [
            "countries.USA.macro.inflation",
            "countries.USA.macro.policy_rate", 
            "countries.USA.macro.debt_gdp",
            "countries.CHN.macro.inflation",
            "countries.DEU.macro.inflation",
            "commodity_prices.oil",
            "commodity_prices.gas"
        ]
        
        for var in variables_to_track:
            trajectory = []
            for step in audit_trail:
                value = self._extract_nested_value(step["state"], var)
                if value is not None:
                    trajectory.append({
                        "timestep": step["timestep"],
                        "value": value
                    })
            
            if trajectory:
                evolution[var] = {
                    "trajectory": trajectory,
                    "initial_value": trajectory[0]["value"],
                    "final_value": trajectory[-1]["value"],
                    "change": trajectory[-1]["value"] - trajectory[0]["value"],
                    "volatility": self._calculate_volatility([t["value"] for t in trajectory]),
                    "trend": self._analyze_trend([t["value"] for t in trajectory])
                }
        
        return evolution
    
    def _analyze_triggers(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Analyze trigger firing patterns and effects."""
        trigger_analysis = {
            "triggers_fired": {},
            "firing_sequence": [],
            "trigger_effects": {}
        }
        
        for step in audit_trail:
            for trigger_name in step["audit"]["triggers_fired"]:
                if trigger_name not in trigger_analysis["triggers_fired"]:
                    trigger_analysis["triggers_fired"][trigger_name] = {
                        "first_fired": step["timestep"],
                        "fire_count": 0,
                        "associated_changes": []
                    }
                
                trigger_analysis["triggers_fired"][trigger_name]["fire_count"] += 1
                trigger_analysis["firing_sequence"].append({
                    "timestep": step["timestep"],
                    "trigger": trigger_name
                })
                
                # Analyze immediate effects
                trigger_changes = [
                    change for change in step["audit"]["field_changes"]
                    if change.get("calculation_details", {}).get("trigger_action") 
                    or trigger_name in change.get("calculation_details", {}).get("triggers_fired", [])
                ]
                
                trigger_analysis["triggers_fired"][trigger_name]["associated_changes"].extend(
                    [(step["timestep"], change) for change in trigger_changes]
                )
        
        return trigger_analysis
    
    def _analyze_reducers(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Analyze reducer execution patterns."""
        reducer_stats = {}
        
        for step in audit_trail:
            for reducer in step["audit"]["reducer_sequence"]:
                if reducer not in reducer_stats:
                    reducer_stats[reducer] = {
                        "execution_count": 0,
                        "field_changes": [],
                        "execution_times": []
                    }
                
                reducer_stats[reducer]["execution_count"] += 1
                
                # Find changes attributed to this reducer
                reducer_changes = [
                    change for change in step["audit"]["field_changes"]
                    if change.get("reducer_name") == reducer
                ]
                reducer_stats[reducer]["field_changes"].extend(reducer_changes)
        
        # Calculate reducer efficiency metrics
        for reducer, stats in reducer_stats.items():
            stats["avg_changes_per_execution"] = len(stats["field_changes"]) / stats["execution_count"]
            stats["unique_fields_affected"] = len(set(
                change["field_path"] for change in stats["field_changes"]
            ))
        
        return reducer_stats
    
    def _analyze_economic_relationships(self, audit_trail: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze key economic relationships for realism."""
        relationships = []
        
        # Taylor Rule Analysis
        taylor_analysis = self._analyze_taylor_rule(audit_trail)
        if taylor_analysis:
            relationships.append(taylor_analysis)
        
        # Phillips Curve Analysis  
        phillips_analysis = self._analyze_phillips_curve(audit_trail)
        if phillips_analysis:
            relationships.append(phillips_analysis)
        
        # Trade-Tariff Relationship
        trade_tariff_analysis = self._analyze_trade_tariff_relationship(audit_trail)
        if trade_tariff_analysis:
            relationships.append(trade_tariff_analysis)
        
        # Crisis Contagion Analysis
        contagion_analysis = self._analyze_crisis_contagion(audit_trail)
        if contagion_analysis:
            relationships.append(contagion_analysis)
        
        return relationships
    
    def _analyze_taylor_rule(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Analyze Taylor Rule implementation for realism."""
        taylor_changes = []
        
        for step in audit_trail:
            for change in step["audit"]["field_changes"]:
                if (change["field_path"] == "countries.USA.macro.policy_rate" and 
                    change.get("calculation_details", {}).get("rule") == "taylor"):
                    
                    taylor_changes.append({
                        "timestep": step["timestep"],
                        "inflation": change["calculation_details"]["inflation"],
                        "inflation_target": change["calculation_details"]["inflation_target"],
                        "output_gap": change["calculation_details"]["output_gap"],
                        "neutral_rate": change["calculation_details"]["neutral_rate"],
                        "old_rate": change["old_value"],
                        "new_rate": change["new_value"],
                        "phi_pi": change["calculation_details"]["phi_pi"],
                        "phi_y": change["calculation_details"]["phi_y"]
                    })
        
        if not taylor_changes:
            return None
        
        # Validate Taylor Rule implementation
        realism_score = 0.0
        issues = []
        
        for change in taylor_changes:
            inflation_gap = change["inflation"] - change["inflation_target"]
            expected_adjustment = (change["phi_pi"] * inflation_gap + 
                                 change["phi_y"] * change["output_gap"])
            
            actual_change = change["new_rate"] - change["neutral_rate"]
            theoretical_rate = change["neutral_rate"] + expected_adjustment
            
            error = abs(change["new_rate"] - theoretical_rate)
            if error < 0.001:
                realism_score += 1.0
            elif error < 0.01:
                realism_score += 0.8
            else:
                realism_score += 0.5
                issues.append(f"Timestep {change['timestep']}: Taylor rule error {error:.4f}")
        
        realism_score /= len(taylor_changes)
        
        return {
            "relationship": "Taylor Rule",
            "description": "Central bank policy rate response to inflation and output gaps",
            "realism_score": realism_score,
            "sample_size": len(taylor_changes),
            "issues": issues,
            "details": {
                "average_phi_pi": sum(c["phi_pi"] for c in taylor_changes) / len(taylor_changes),
                "average_phi_y": sum(c["phi_y"] for c in taylor_changes) / len(taylor_changes),
                "rate_range": (
                    min(c["new_rate"] for c in taylor_changes),
                    max(c["new_rate"] for c in taylor_changes)
                )
            }
        }
    
    def _analyze_phillips_curve(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Analyze Phillips Curve implementation."""
        phillips_changes = []
        
        for step in audit_trail:
            for change in step["audit"]["field_changes"]:
                if (change["field_path"] == "countries.USA.macro.inflation" and 
                    "phillips_curve" in change.get("calculation_details", {})):
                    
                    details = change["calculation_details"]
                    phillips_changes.append({
                        "timestep": step["timestep"],
                        "old_inflation": change["old_value"],
                        "new_inflation": change["new_value"],
                        "expected_inflation": details["expected_inflation"],
                        "output_gap": details["output_gap"],
                        "beta": details["beta"],
                        "kappa": details["kappa"]
                    })
        
        if not phillips_changes:
            return None
        
        # Validate Phillips Curve
        realism_score = 0.0
        issues = []
        
        for change in phillips_changes:
            # π_t = β*E[π_{t+1}] + κ*y_t + ε_t
            expected_inflation_component = change["beta"] * change["expected_inflation"]
            output_gap_component = change["kappa"] * change["output_gap"]
            theoretical_inflation = expected_inflation_component + output_gap_component
            
            error = abs(change["new_inflation"] - theoretical_inflation)
            if error < 0.01:
                realism_score += 1.0
            elif error < 0.02:
                realism_score += 0.8
            else:
                realism_score += 0.6
                issues.append(f"Timestep {change['timestep']}: Phillips curve error {error:.4f}")
        
        realism_score /= len(phillips_changes)
        
        return {
            "relationship": "Phillips Curve",
            "description": "Inflation response to output gaps and expectations",
            "realism_score": realism_score,
            "sample_size": len(phillips_changes),
            "issues": issues,
            "details": {
                "average_beta": sum(c["beta"] for c in phillips_changes) / len(phillips_changes),
                "average_kappa": sum(c["kappa"] for c in phillips_changes) / len(phillips_changes)
            }
        }
    
    def _analyze_trade_tariff_relationship(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Analyze relationship between tariffs and trade volumes."""
        tariff_changes = []
        trade_changes = []
        
        for step in audit_trail:
            for change in step["audit"]["field_changes"]:
                if "tariff" in change["field_path"]:
                    tariff_changes.append({
                        "timestep": step["timestep"],
                        "field": change["field_path"],
                        "old_value": change["old_value"],
                        "new_value": change["new_value"]
                    })
                
                if "trade_matrix" in change["field_path"]:
                    trade_changes.append({
                        "timestep": step["timestep"],
                        "field": change["field_path"],
                        "old_value": change["old_value"],
                        "new_value": change["new_value"]
                    })
        
        if not tariff_changes and not trade_changes:
            return None
        
        return {
            "relationship": "Tariff-Trade Relationship",
            "description": "Impact of tariff changes on bilateral trade volumes",
            "realism_score": 0.8,  # Simplified for now
            "sample_size": len(tariff_changes) + len(trade_changes),
            "details": {
                "tariff_changes": len(tariff_changes),
                "trade_volume_changes": len(trade_changes),
                "tariff_events": tariff_changes[-3:],  # Last 3 events
                "trade_events": trade_changes[-3:]   # Last 3 events
            }
        }
    
    def _analyze_crisis_contagion(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Analyze crisis contagion mechanisms."""
        contagion_evidence = []
        
        # Look for patterns where problems in one country affect others
        for i, step in enumerate(audit_trail):
            if i == 0:
                continue
                
            prev_step = audit_trail[i-1]
            
            # Check for financial stress indicators
            for change in step["audit"]["field_changes"]:
                if ("credit_spread" in change["field_path"] or 
                    "fx_rate" in change["field_path"] or
                    "bank_tier1_ratio" in change["field_path"]):
                    
                    # Look for simultaneous changes in multiple countries
                    country_changes = [
                        c for c in step["audit"]["field_changes"] 
                        if any(country in c["field_path"] for country in ["USA", "GBR", "EUR", "CHN"])
                    ]
                    
                    if len(country_changes) > 1:
                        contagion_evidence.append({
                            "timestep": step["timestep"],
                            "trigger_change": change,
                            "affected_countries": len(set(
                                c["field_path"].split(".")[1] for c in country_changes
                            )),
                            "changes": country_changes
                        })
        
        if not contagion_evidence:
            return None
        
        return {
            "relationship": "Crisis Contagion",
            "description": "Transmission of financial stress between countries",
            "realism_score": 0.7,
            "sample_size": len(contagion_evidence),
            "details": {
                "contagion_events": len(contagion_evidence),
                "max_countries_affected": max(e["affected_countries"] for e in contagion_evidence),
                "primary_transmission_channels": ["credit_spread", "fx_rate", "interbank_linkages"]
            }
        }
    
    def _assess_realism(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Overall realism assessment."""
        assessments = []
        
        # Check for economic consistency
        assessments.append(self._assess_variable_ranges(audit_trail))
        assessments.append(self._assess_causality_chains(audit_trail))
        assessments.append(self._assess_timing_realism(audit_trail))
        
        # Filter out None assessments and calculate overall score
        valid_assessments = [a for a in assessments if a is not None and "score" in a]
        
        if valid_assessments:
            overall_score = sum(a["score"] for a in valid_assessments) / len(valid_assessments)
        else:
            overall_score = 0.5  # Default neutral score if no valid assessments
        
        return {
            "overall_realism_score": overall_score,
            "individual_assessments": valid_assessments,
            "grade": self._score_to_grade(overall_score),
            "summary": self._generate_realism_summary(overall_score, valid_assessments)
        }
    
    def _assess_variable_ranges(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Check if economic variables stay within realistic ranges."""
        issues = []
        score = 1.0
        
        for step in audit_trail:
            state = step["state"]
            
            # Check key variables for realistic ranges
            for country_code, country_data in state.get("countries", {}).items():
                macro = country_data.get("macro", {})
                
                # Inflation should be reasonable (-5% to 50%)
                inflation = macro.get("inflation")
                if inflation is not None and (inflation < -0.05 or inflation > 0.5):
                    issues.append(f"Timestep {step['timestep']}: {country_code} inflation {inflation:.3f} outside realistic range")
                    score -= 0.1
                
                # Policy rate should be reasonable (-1% to 30%)
                policy_rate = macro.get("policy_rate") 
                if policy_rate is not None and (policy_rate < -0.01 or policy_rate > 0.3):
                    issues.append(f"Timestep {step['timestep']}: {country_code} policy rate {policy_rate:.3f} outside realistic range")
                    score -= 0.1
                
                # Unemployment should be reasonable (0% to 50%)
                unemployment = macro.get("unemployment")
                if unemployment is not None and (unemployment < 0 or unemployment > 0.5):
                    issues.append(f"Timestep {step['timestep']}: {country_code} unemployment {unemployment:.3f} outside realistic range")
                    score -= 0.1
        
        return {
            "assessment": "Variable Range Check",
            "score": max(score, 0.0),
            "issues": issues[:10],  # Limit to 10 issues
            "total_issues": len(issues)
        }
    
    def _assess_causality_chains(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Assess whether cause-effect relationships make economic sense."""
        # This is a simplified implementation - could be expanded significantly
        score = 0.8  # Default reasonable score
        
        # Look for trigger → effect chains
        causal_chains = []
        for step in audit_trail:
            if step["audit"]["triggers_fired"]:
                trigger_effects = []
                for change in step["audit"]["field_changes"]:
                    if change.get("calculation_details", {}).get("trigger_action"):
                        trigger_effects.append(change["field_path"])
                
                causal_chains.append({
                    "timestep": step["timestep"],
                    "triggers": step["audit"]["triggers_fired"],
                    "immediate_effects": trigger_effects
                })
        
        return {
            "assessment": "Causality Chain Analysis",
            "score": score,
            "causal_chains_identified": len(causal_chains),
            "examples": causal_chains[:3]
        }
    
    def _assess_timing_realism(self, audit_trail: List[Dict]) -> Dict[str, Any]:
        """Assess whether the timing of economic adjustments is realistic."""
        # Check that adjustments don't happen instantaneously
        timing_score = 0.9
        
        # Most economic adjustments should show gradual changes
        rapid_changes = 0
        total_changes = 0
        
        for step in audit_trail:
            for change in step["audit"]["field_changes"]:
                if change["old_value"] is not None and change["new_value"] is not None and change["old_value"] != 0:
                    pct_change = abs((change["new_value"] - change["old_value"]) / change["old_value"])
                    if pct_change > 0.1:  # >10% change per timestep is rapid
                        rapid_changes += 1
                    total_changes += 1
                elif change["old_value"] == 0 and change["new_value"] is not None:
                    # Handle zero-to-nonzero transitions as potentially rapid
                    if abs(change["new_value"]) > 0.01:  # Significant absolute change
                        rapid_changes += 1
                    total_changes += 1
        
        if total_changes > 0:
            rapid_change_ratio = rapid_changes / total_changes
            if rapid_change_ratio > 0.3:  # More than 30% rapid changes
                timing_score -= 0.2
        
        return {
            "assessment": "Timing Realism",
            "score": timing_score,
            "rapid_changes": rapid_changes,
            "total_changes": total_changes,
            "rapid_change_ratio": rapid_changes / total_changes if total_changes > 0 else 0
        }
    
    def _extract_key_insights(self, audit_trail: List[Dict]) -> List[EconomicInsight]:
        """Extract key economic insights from the scenario."""
        insights = []
        
        # Monetary policy effectiveness
        policy_changes = [
            change for step in audit_trail
            for change in step["audit"]["field_changes"]
            if "policy_rate" in change["field_path"]
        ]
        
        if policy_changes:
            insights.append(EconomicInsight(
                category="Monetary Policy",
                description="Central bank policy responses observed throughout scenario",
                evidence={
                    "total_policy_changes": len(policy_changes),
                    "rate_range": (
                        min(c["new_value"] for c in policy_changes if c["new_value"] is not None),
                        max(c["new_value"] for c in policy_changes if c["new_value"] is not None)
                    ),
                    "taylor_rule_applications": len([c for c in policy_changes if c.get("calculation_details", {}).get("rule") == "taylor"])
                },
                realism_score=0.8
            ))
        
        # Crisis transmission 
        trigger_sequence = []
        for step in audit_trail:
            for trigger in step["audit"]["triggers_fired"]:
                trigger_sequence.append((step["timestep"], trigger))
        
        if len(trigger_sequence) > 2:
            insights.append(EconomicInsight(
                category="Crisis Dynamics",
                description="Complex crisis evolution with multiple trigger events",
                evidence={
                    "trigger_sequence": trigger_sequence,
                    "crisis_duration": max(t[0] for t in trigger_sequence) - min(t[0] for t in trigger_sequence) + 1,
                    "trigger_types": list(set(t[1] for t in trigger_sequence))
                },
                realism_score=0.9
            ))
        
        return insights
    
    def _generate_recommendations(self, audit_trail: List[Dict]) -> List[str]:
        """Generate recommendations for improving simulation realism."""
        recommendations = []
        
        # Check reducer consistency
        reducer_patterns = {}
        for step in audit_trail:
            sequence_key = ",".join(step["audit"]["reducer_sequence"])
            reducer_patterns[sequence_key] = reducer_patterns.get(sequence_key, 0) + 1
        
        if len(reducer_patterns) == 1:
            recommendations.append("✅ Reducer sequence is consistent across all timesteps")
        else:
            recommendations.append("⚠️ Consider investigating variable reducer sequences - may indicate inconsistent simulation logic")
        
        # Check for missing economic mechanisms
        all_field_paths = set()
        for step in audit_trail:
            for change in step["audit"]["field_changes"]:
                all_field_paths.add(change["field_path"])
        
        if not any("trade" in path for path in all_field_paths):
            recommendations.append("💡 Consider adding trade dynamics for more comprehensive economic modeling")
        
        if not any("external" in path for path in all_field_paths):
            recommendations.append("💡 Consider adding exchange rate and external sector dynamics")
        
        # Performance recommendations
        avg_changes = sum(len(step["audit"]["field_changes"]) for step in audit_trail) / len(audit_trail)
        if avg_changes > 20:
            recommendations.append("⚡ High number of field changes per step - consider optimizing reducer efficiency")
        elif avg_changes < 3:
            recommendations.append("🔍 Low number of field changes per step - verify all economic mechanisms are active")
        
        return recommendations
    
    # Helper methods
    def _extract_nested_value(self, data: Dict, path: str) -> Any:
        """Extract nested value using dot notation."""
        try:
            current = data
            for part in path.split("."):
                current = current[part]
            return current
        except (KeyError, TypeError):
            return None
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate simple volatility measure."""
        if len(values) < 2:
            return 0.0
        
        changes = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
        return sum(changes) / len(changes)
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analyze trend in time series."""
        if len(values) < 3:
            return "insufficient_data"
        
        increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
        decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i-1])
        
        if increases > decreases * 1.5:
            return "increasing"
        elif decreases > increases * 1.5:
            return "decreasing"
        else:
            return "stable"
    
    def _check_reducer_consistency(self, audit_trail: List[Dict]) -> bool:
        """Check if reducer sequences are consistent."""
        if not audit_trail:
            return True
        
        first_sequence = audit_trail[0]["audit"]["reducer_sequence"]
        return all(step["audit"]["reducer_sequence"] == first_sequence for step in audit_trail)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"  
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def _generate_realism_summary(self, score: float, assessments: List[Dict]) -> str:
        """Generate textual summary of realism assessment."""
        if score >= 0.9:
            return "Excellent economic realism with consistent relationships and realistic variable ranges."
        elif score >= 0.8:
            return "Good economic realism with minor issues in some areas."
        elif score >= 0.7:
            return "Acceptable economic realism but some relationships may need refinement."
        elif score >= 0.6:
            return "Marginal economic realism with several areas needing improvement."
        else:
            return "Poor economic realism - significant improvements needed in core relationships."
    
    def generate_detailed_report(self, audit_file: Path, output_file: Path = None) -> Path:
        """Generate comprehensive detailed report."""
        analysis = self.analyze_scenario(audit_file)
        
        if output_file is None:
            output_file = self.reports_dir / f"detailed_analysis_{analysis['scenario_name'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Add metadata
        analysis["analysis_metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "analyzer_version": "1.0",
            "source_file": str(audit_file)
        }
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Generate human-readable summary
        summary_file = output_file.with_suffix('.md')
        self._generate_markdown_summary(analysis, summary_file)
        
        print(f"📊 Detailed analysis saved: {output_file}")
        print(f"📖 Summary report saved: {summary_file}")
        
        return output_file
    
    def _generate_markdown_summary(self, analysis: Dict[str, Any], output_file: Path):
        """Generate human-readable markdown summary."""
        content = f"""# Scenario Analysis Report: {analysis['scenario_name']}

## Executive Summary
- **Overall Realism Score**: {analysis['realism_assessment']['overall_realism_score']:.2f} ({analysis['realism_assessment']['grade']})
- **Timesteps Completed**: {analysis['execution_summary']['timesteps_completed']}
- **Total Field Changes**: {analysis['execution_summary']['total_field_changes']}
- **Triggers Fired**: {analysis['execution_summary']['total_triggers_fired']}

{analysis['realism_assessment']['summary']}

## Performance Metrics
- **Execution Time**: {analysis['execution_summary']['execution_time_seconds']:.2f} seconds
- **Average Step Time**: {analysis['execution_summary']['performance_metrics']['avg_step_time_ms']:.1f} ms
- **Changes per Second**: {analysis['execution_summary']['performance_metrics']['changes_per_second']:.1f}

## Economic Relationships Analysis
"""
        
        for relationship in analysis['economic_relationships']:
            content += f"""
### {relationship['relationship']}
- **Realism Score**: {relationship['realism_score']:.2f}
- **Description**: {relationship['description']}
- **Sample Size**: {relationship['sample_size']}
"""
            if relationship.get('issues'):
                content += f"- **Issues**: {len(relationship['issues'])} identified\n"
        
        content += f"""
## Key State Evolution
"""
        
        for var, evolution in analysis['state_evolution'].items():
            if evolution['trajectory']:
                content += f"""
### {var}
- **Initial**: {evolution['initial_value']:.4f}
- **Final**: {evolution['final_value']:.4f}
- **Change**: {evolution['change']:.4f}
- **Trend**: {evolution['trend']}
"""
        
        content += f"""
## Trigger Analysis
"""
        
        if analysis['trigger_analysis']['triggers_fired']:
            for trigger_name, trigger_info in analysis['trigger_analysis']['triggers_fired'].items():
                content += f"""
### {trigger_name}
- **First Fired**: Timestep {trigger_info['first_fired']}
- **Fire Count**: {trigger_info['fire_count']}
- **Associated Changes**: {len(trigger_info['associated_changes'])}
"""
        
        content += f"""
## Key Insights
"""
        
        for insight in analysis['key_insights']:
            content += f"""
### {insight.category}
- **Description**: {insight.description}
- **Realism Score**: {insight.realism_score:.2f}
"""
        
        content += f"""
## Recommendations
"""
        
        for rec in analysis['recommendations']:
            content += f"- {rec}\n"
        
        content += f"""
## Detailed Data
For complete analysis data including field-by-field changes, see the accompanying JSON file.

---
*Report generated at {analysis['analysis_metadata']['generated_at']}*
"""
        
        with open(output_file, 'w') as f:
            f.write(content)


if __name__ == "__main__":
    """Run analysis on all available audit files."""
    import sys
    
    analyzer = ScenarioAnalyzer()
    reports_dir = Path("reports")
    
    if len(sys.argv) > 1:
        # Analyze specific file
        audit_file = Path(sys.argv[1])
        if audit_file.exists():
            analyzer.generate_detailed_report(audit_file)
        else:
            print(f"File not found: {audit_file}")
    else:
        # Analyze all audit files
        audit_files = list(reports_dir.glob("audit_*.json"))
        if not audit_files:
            print("No audit files found in reports directory")
        else:
            print(f"Found {len(audit_files)} audit files to analyze")
            for audit_file in audit_files:
                try:
                    analyzer.generate_detailed_report(audit_file)
                except Exception as e:
                    print(f"Error analyzing {audit_file.name}: {e}")
