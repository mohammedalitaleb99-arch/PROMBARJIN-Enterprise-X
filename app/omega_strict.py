from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable
from datetime import datetime, timezone
import re
import math

SPEC_VERSION = "1.0"
QUALITY_TARGET = 95.0
PRIORITIES = ["truth", "safety", "accuracy", "logical_consistency", "evidence_quality", "completeness", "executive_utility", "efficiency"]
DOMAINS = ["finance", "corporate finance", "fp&a", "investment", "accounting", "mining", "critical minerals", "antimony", "oil & gas", "commodity trading", "supply chain", "economics", "strategy", "esg", "risk", "negotiation", "research", "writing", "coding", "legal analysis", "scientific analysis", "engineering"]
OUTPUT_MODES = ["executive brief", "technical report", "deep analysis", "decision memo", "academic style", "business proposal", "implementation plan", "step-by-step guide", "comparative matrix"]
BIAS_TYPES = ["confirmation bias", "anchoring", "availability bias", "authority bias", "survivorship bias", "recency bias", "optimism bias", "groupthink"]
RISK_TYPES = ["strategic", "financial", "operational", "legal", "compliance", "technology", "supply", "geopolitical", "cyber", "esg"]
MINING_UNITS = ["%", "ppm", "g/t", "kg/t", "MT", "DMT", "WMT", "lb", "ton", "oz"]
PENALTY_ELEMENTS = ["As", "Hg", "Pb", "Cd", "Bi", "F", "Cl", "Se", "Te", "Cu", "Zn", "Fe", "S"]
ENERGY_FRAMEWORKS = ["IFRS S1", "IFRS S2", "GRI", "SASB", "TCFD", "ISSB", "CSRD", "GHG Protocol", "CDP", "UN SDGs"]
PLACEHOLDER_MARKERS = ("TODO", "FIXME", "TBD", "PLACEHOLDER", "IMPLEMENT LATER", "define mitigation", "assess", "task-defined")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def missing(field: str, reason: str) -> dict[str, Any]:
    return {"status": "MISSING_DATA_REQUIRED", "field": field, "reason": reason, "verification_required": True}


def safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b in (None, 0):
        return None
    return a / b


def classification(text: str) -> dict[str, Any]:
    t = text.lower()
    matches = [d for d in DOMAINS if d in t]
    if "oil & gas" in t or ("oil" in t and "gas" in t):
        primary = "oil & gas"
    elif any(k in t for k in ["finance", "investment", "accounting", "npv", "irr", "valuation", "financial"]):
        primary = "finance"
    elif matches:
        primary = matches[0]
    else:
        primary = "general"
    secondary = [d for d in matches if d != primary]
    mission = "research" if any(k in t for k in ["research", "investigate", "sources", "verify"] ) else ("decision" if any(k in t for k in ["should we", "recommend", "decision", "choose"]) else "analysis")
    complexity = "high" if len(text) > 1200 or len(matches) >= 3 else ("medium" if matches else "low")
    risk = "high" if any(k in t for k in ["legal", "regulatory", "investment", "safety", "contract", "compliance", "high risk"]) else ("medium" if matches else "low")
    evidence = "high" if risk == "high" or mission == "research" or any(k in t for k in ["evidence", "source", "verify"]) else "medium"
    depth = "maximum precision" if risk == "high" else ("deep" if complexity == "high" else "balanced")
    output = "decision memo" if any(k in t for k in ["memo", "board memo", "decision memo"]) else next((m for m in OUTPUT_MODES if m in t), "executive brief")
    return {"primary_domain": primary, "secondary_domains": secondary, "complexity": complexity, "urgency": "high" if any(k in t for k in ["urgent", "today", "critical", "deadline"]) else "normal", "decision_risk": risk, "evidence_requirement": evidence, "required_depth": depth, "expected_output": output, "mission": mission}


def problem_model(text: str, profile: dict[str, Any]) -> dict[str, Any]:
    return {"problem": text.strip(), "goal": "Produce a verified, decision-useful result", "desired_outcome": "Decision-ready deliverable", "constraints": [], "unknown_variables": [], "stakeholders": [], "risk_level": profile["decision_risk"], "decision_type": profile["mission"]}


def first_order(text: str) -> dict[str, Any]:
    return {"immediate_effects": ["direct_effects_required_from_evidence"], "direct_consequences": ["direct_consequences_required_from_evidence"], "expected_benefits": ["benefits_required_from_evidence"], "expected_costs": ["costs_required_from_evidence"]}


def second_order() -> dict[str, Any]:
    return {"indirect_effects": ["indirect_effects_required_from_evidence"], "delayed_effects": ["delayed_effects_required_from_evidence"], "hidden_tradeoffs": ["hidden_tradeoffs_required_from_evidence"], "opportunity_cost": ["opportunity_cost_required_from_data"], "feedback_loops": ["feedback_loops_required_from_system_map"]}


def third_order() -> dict[str, Any]:
    return {"long_term_impact": ["long_term_impact_required_from_evidence"], "strategic_consequences": ["strategic_consequences_required_from_evidence"], "behavioral_reactions": ["behavioral_reactions_required_from_stakeholders"], "market_reactions": ["market_reactions_required_from_market_data"], "system_dynamics": ["system_dynamics_required_from_dependencies"]}


def system_map() -> dict[str, list[str]]:
    return {k: [] for k in ["inputs", "processes", "dependencies", "constraints", "outputs", "feedback", "failure_points"]}


def root_cause(text: str) -> dict[str, Any]:
    return {"five_whys": [f"Why {i}: causal investigation required" for i in range(1, 6)], "fishbone": {k: [] for k in ["People", "Process", "Technology", "Materials", "Measurement", "Environment"]}, "fault_tree": {"top_event": text, "gates": {"OR": ["people", "process", "technology", "external"]}}, "constraint_analysis": []}


def counterfactuals() -> dict[str, Any]:
    return {"scenario_a": "key assumption improves", "scenario_b": "key assumption worsens", "scenario_c": "key assumption reverses", "best_case": "best supported case", "worst_case": "worst supported case", "most_likely_case": "base-rate supported case"}


def hypotheses(text: str) -> list[dict[str, Any]]:
    return [
        {"id": "H1", "type": "primary", "statement": f"Primary explanation for: {text}", "rank": 1},
        {"id": "H2", "type": "alternative", "statement": "External/environmental driver", "rank": 2},
        {"id": "H3", "type": "alternative", "statement": "Data/measurement/definition issue", "rank": 3},
        {"id": "H4", "type": "alternative", "statement": "Incentive/behavior/strategy driver", "rank": 4},
    ]


def assumptions(text: str) -> list[dict[str, Any]]:
    terms = [s.strip() for s in re.split(r"[.;]", text) if s.strip()]
    candidates = [s for s in terms if re.search(r"\b(assume|assuming|likely|may|might|could|expected)\b", s, re.I)]
    return [{"id": f"ASM-{i+1}", "text": s, "confidence": None, "evidence": None, "verification_method": "source_or_calculation_required"} for i, s in enumerate(candidates)]


def bias_firewall(text: str) -> list[dict[str, Any]]:
    t = text.lower()
    return [{"bias": b, "detected": b in t, "corrective_action": "counter-test required" if b in t else "monitor"} for b in BIAS_TYPES]


def information_asymmetry() -> dict[str, list[str]]:
    return {"missing_information": [], "unknown_unknowns": [], "blind_spots": [], "hidden_incentives": []}


def decision_impact() -> dict[str, Any]:
    return {k: missing(k, "impact data not supplied") for k in ["financial", "operational", "strategic", "reputation", "legal", "esg"]}


def research_runtime() -> dict[str, Any]:
    return {"planning": {"primary_research_question": None, "secondary_questions": [], "known_facts": [], "unknown_facts": [], "critical_unknowns": [], "research_scope": None, "time_horizon": None, "evidence_threshold": QUALITY_TARGET}, "source_levels": {"A": [], "B": [], "C": [], "D": []}, "iterative_stop_conditions": ["information_saturation", "evidence_confidence_ge_95", "no_new_meaningful_evidence"], "contradiction_detection": True, "citation_graph": True, "knowledge_gap_detection": True, "red_team": True, "confidence_calibration": True, "quality_gate": True}


def decision_runtime() -> dict[str, Any]:
    opts = []
    for i in range(5): opts.append({"id": f"R{i+1}", "type": "realistic", "status": "option"})
    opts += [{"id": "U1", "type": "unconventional", "status": "option"}, {"id": "U2", "type": "unconventional", "status": "option"}, {"id": "D1", "type": "disruptive", "status": "option"}]
    return {"decision_definition": {k: None for k in ["decision_owner", "decision_objective", "decision_horizon", "decision_constraints", "critical_success_factors", "failure_criteria", "reversibility", "cost_of_delay"]}, "options": opts, "option_score_fields": ["strategic_value","financial_value","operational_complexity","implementation_time","capital_requirement","execution_risk","scalability","resilience","expected_roi","expected_npv","confidence"], "scenario_set": ["best_case","expected_case","worst_case","stress_case","black_swan_case"], "risk_categories": RISK_TYPES, "monte_carlo": {"status": "ready", "variables": [], "distributions": [], "sensitivity_drivers": [], "critical_thresholds": []}, "second_order_validation": True, "impact_dimensions": ["profitability","liquidity","growth","customers","employees","suppliers","investors","reputation","compliance","long_term_strategy"]}


def npv(rate: float, cashflows: list[float]) -> float:
    if rate <= -1: raise ValueError("invalid_discount_rate")
    return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))


def irr(cashflows: list[float]) -> float | None:
    if not any(x < 0 for x in cashflows) or not any(x > 0 for x in cashflows): return None
    lo, hi = -0.9999, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        v = npv(mid, cashflows)
        if abs(v) < 1e-9: return mid
        if v > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def modified_irr(cashflows: list[float], finance_rate: float, reinvest_rate: float) -> float | None:
    n = len(cashflows) - 1
    if n <= 0: return None
    pv = sum(cf / ((1 + finance_rate) ** i) for i, cf in enumerate(cashflows) if cf < 0)
    fv = sum(cf * ((1 + reinvest_rate) ** (n - i)) for i, cf in enumerate(cashflows) if cf > 0)
    return None if pv == 0 or fv < 0 else (fv / (-pv)) ** (1 / n) - 1


def payback(cashflows: list[float]) -> float | None:
    cumulative = 0.0
    for i, cf in enumerate(cashflows):
        prev = cumulative; cumulative += cf
        if prev < 0 <= cumulative and cf != 0:
            return i - 1 + (-prev / cf)
    return None


def discounted_payback(rate: float, cashflows: list[float]) -> float | None:
    return payback([cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows)])


def profitability_index(rate: float, cashflows: list[float]) -> float | None:
    if not cashflows or cashflows[0] >= 0: return None
    future_pv = sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows[1:], start=1))
    return future_pv / (-cashflows[0])


def financial_runtime() -> dict[str, Any]:
    return {"roles": ["CFO","FP&A Director","Corporate Finance Director","Investment Banker","Private Equity Analyst","Equity Research Analyst","Credit Analyst","Risk Manager","Treasury Manager","M&A Advisor","Mining Finance Specialist","Commodity Trading Finance Specialist","Oil & Gas Financial Analyst"], "diagnostic": ["Revenue","Gross Margin","EBITDA","Operating Margin","Net Margin","Cash Flow","Working Capital","Liquidity","Leverage","Profitability","Capital Structure","Growth","Operational Efficiency","Capital Allocation"], "ratios": ["Current Ratio","Quick Ratio","Cash Ratio","Debt Ratio","Debt to Equity","Interest Coverage","ROA","ROE","ROIC","ROCE","Gross Margin","Operating Margin","Net Margin","Asset Turnover","Inventory Turnover","Receivable Days","Payable Days","Cash Conversion Cycle"], "valuations": ["DCF","Comparable Companies","Comparable Transactions","NAV","Replacement Cost","Residual Income","Dividend Discount","Real Options","Commodity Asset Valuation","Mining Asset Valuation"], "capital_budgeting": ["NPV","IRR","Modified IRR","Payback","Discounted Payback","Profitability Index","Sensitivity Analysis","Scenario Analysis"], "forecast": ["Revenue Forecast","Cost Forecast","EBITDA Forecast","Cash Flow Forecast","Balance Sheet Projection","Working Capital Projection","Capital Expenditure Projection"], "risk": ["Liquidity Risk","Credit Risk","Market Risk","Operational Risk","Commodity Price Risk","Interest Rate Risk","FX Risk","Political Risk","Country Risk","Counterparty Risk"], "stress_cases": ["Base Case","Best Case","Worst Case","Stress Case","Extreme Case"], "quality_controls": ["numbers","units","currency","accounting_treatment","assumptions","cashflow_vs_income","balance_sheet_balance"]}


def mining_runtime() -> dict[str, Any]:
    return {"domains": ["Mining","Critical Minerals","Rare Metals","Antimony","Tin","Tungsten","Copper","Lithium","Nickel","Cobalt","Graphite","Rare Earth Elements","Commodity Trading","Metal Concentrates","Mining Finance","JORC","NI43-101","SAMREC"], "identification": ["Commodity","Deposit Type","Ore Type","Concentrate","Metal","Ore Grade","Country","Mining Stage","Processing Stage","Trading Stage"], "ore_quality": ["Head Grade","Recoverable Grade","Payable Grade","Recovery %","Moisture","Density","Particle Size","Liberation","Penalty Elements"], "penalties": PENALTY_ELEMENTS, "metallurgy": ["Gravity Recovery","Flotation","Leaching","Roasting","Hydrometallurgy","Pyrometallurgy","Recovery Constraints","Processing Bottlenecks"], "resources": ["Measured","Indicated","Inferred","Probable Reserve","Proved Reserve","JORC Compliance","NI43-101 Compliance","Data Confidence"], "trading": ["FOB","CIF","DAP","CFR","EXW","Container","Bulk Shipment","Insurance","Freight","Port Risk","Logistics Risk"], "payability": ["Reference Metal Price","Payability %","Treatment Charges","Refining Charges","Penalties","Bonuses","Net Smelter Return","Expected Revenue"], "price": ["Spot Price","Forward Price","Contract Price","Benchmark Price","Premium","Discount","Regional Premium"], "market": ["Supply","Demand","Inventory","Strategic Stockpiles","Government Policy","Export Controls","Import Restrictions","Sanctions","Substitution Risk","Recycling Impact"], "country_risk": ["Political Risk","Currency Risk","Infrastructure","Port Capacity","Power Availability","Security","Legal Framework","Mining Code"], "offtake": ["Counterparty Quality","Credit Risk","Payment Terms","Delivery Schedule","Force Majeure","Termination Clauses","Pricing Formula","Dispute Resolution"], "contract": ["Units","Currency","Incoterms","Grade Basis","Moisture Basis","Sampling Method","Assay Method","Arbitration Rules","Commercial Definitions"], "units": MINING_UNITS}


def energy_runtime() -> dict[str, Any]:
    return {"sector": ["Industry","Subsector","Value Chain","Business Model","Asset Type","Ownership Structure","Revenue Drivers","Cost Drivers"], "value_chain": ["Upstream","Midstream","Downstream","Integrated","Trading","Storage","Distribution","Retail","Supporting Services"], "upstream": ["Exploration","Development","Production","Reserve Life","Reserve Replacement Ratio","Decline Curve","Production Cost","Lifting Cost","Finding Cost","Reserve Risk"], "midstream": ["Pipeline","Terminal","LNG","Storage","Transportation","Compression","Infrastructure Risk","Capacity Utilization"], "downstream": ["Refining","Petrochemicals","Marketing","Retail","Distribution","Refining Margin","Crack Spread","Product Yield"], "market": ["Supply","Demand","Inventories","OPEC+","Geopolitical Events","Shipping","Freight","Weather","Seasonality","Strategic Reserves"], "prices": ["WTI","Brent","Dubai","Henry Hub","TTF","JKM","Coal","Electricity","Carbon","Hydrogen"], "project_economics": ["CapEx","OpEx","NPV","IRR","Payback","Breakeven","Sensitivity","Risk Premium","Capital Efficiency"], "esg": ["Environmental","Social","Governance","Materiality","Climate Risk","Water Risk","Waste","Tailings","Methane","Biodiversity","Human Rights","Community Impact","Supply Chain"], "climate": ["Transition Risk","Physical Risk","Carbon Exposure","Carbon Price","Climate Scenario","Decarbonization Pathway","Net Zero Alignment"], "reporting": ENERGY_FRAMEWORKS, "risk": ["Commodity Risk","Political Risk","Reserve Risk","Operational Risk","Regulatory Risk","Environmental Risk","Technology Risk","Counterparty Risk"], "portfolio": ["Portfolio Diversification","Asset Allocation","Risk Concentration","Commodity Exposure","Geographic Exposure","Capital Allocation"]}


def memory_runtime() -> dict[str, Any]:
    return {"session_memory": ["Conversation Goal","Completed Tasks","Pending Tasks","Open Questions","Assumptions","Constraints","User Preferences","Executive Decisions","Knowledge Acquired"], "compression": ["Semantic Compression","Decision Compression","Evidence Compression","Task Compression"], "hierarchy": ["Current Message","Current Session","Project Context","Persistent Knowledge","Executive Decision History"], "priority": ["User Objective","Verified Facts","Executive Decisions","Critical Constraints","Supporting Context"], "knowledge_graph": ["Entities","Companies","People","Projects","Countries","Commodities","Contracts","Relationships","Dependencies","Confidence"], "decision_ledger": ["Decision ID","Decision","Reason","Evidence","Confidence","Timestamp","Dependencies","Reversal Conditions"], "anti_degradation": ["Instruction Drift","Reasoning Drift","Context Drift","Memory Drift","Domain Drift","Logic Drift","Terminology Drift","Quality Drift"], "self_audit": ["Objective Alignment","Instruction Alignment","Context Alignment","Reasoning Quality","Evidence Quality","Consistency","Completeness"]}


def governance_runtime() -> dict[str, Any]:
    return {"levels": ["A","B","C","D","E"], "level_definitions": {"A":"Verified Primary Evidence","B":"Verified Secondary Evidence","C":"Reasonable Inference","D":"Hypothesis","E":"Speculation"}, "temporal": ["Publication Date","Revision Date","Current Validity","Expiration Risk","Market Freshness","Regulatory Freshness","Technology Freshness"], "evidence": ["Evidence Source","Evidence Quality","Evidence Independence","Evidence Freshness","Replication Status","Conflict Status","Evidence Confidence"], "decision_gate": ["Evidence Sufficiency","Logical Consistency","Strategic Consistency","Operational Feasibility","Financial Plausibility","Risk Assessment","Implementation Realism"], "numerical": ["Arithmetic","Units","Percentages","Currencies","Dates","Conversions","Totals","Ranges","Tolerance"], "audit": ["Finding ID","Evidence ID","Decision ID","Assumption ID","Calculation ID","Risk ID","Validation Status","Dependency Chain"], "consistency": ["Terminology","Definitions","Units","Entity Names","Company Names","Country Names","Commodity Names","Project Names","Abbreviations"], "contradictions": ["Logical Contradictions","Numerical Contradictions","Evidence Contradictions","Timeline Contradictions","Domain Contradictions"], "uncertainty": ["Known Unknowns","Critical Unknowns","Confidence Drivers","Confidence Limiters","Evidence Gaps","Required Validation"], "hallucination": ["facts","quotations","statistics","regulations","company information","research","citations"], "quality_metrics": ["Accuracy","Evidence","Depth","Reasoning","Consistency","Completeness","Executive Value","Actionability","Traceability"]}


def output_runtime() -> dict[str, Any]:
    return {"profiles": ["Executive","Technical","Scientific","Financial","Legal","Negotiation","Research","Educational","Consulting","Coding","Presentation","Proposal","Report"], "density": ["Tiny","Short","Medium","Long","Executive","Comprehensive","Book-Level"], "structure": ["Executive Summary","Key Findings","Evidence","Analysis","Options","Risk Matrix","Recommendation","Implementation","Confidence"], "actions": ["Immediate Actions","30-Day Plan","90-Day Plan","Long-Term Roadmap","KPIs","Milestones"], "visual": ["Tables","Decision Trees","Matrices","Frameworks","Bullet Hierarchies","Timelines","Comparison Charts","Risk Maps","Process Maps"], "quality": ["Formatting","Flow","Consistency","Terminology","Executive Readability","Decision Readiness","Implementation Readiness"]}


def strict_release_gate(report: dict[str, Any], evidence_count: int = 0) -> dict[str, Any]:
    issues: list[str] = []
    serialized = repr(report)
    for marker in PLACEHOLDER_MARKERS:
        if marker in serialized and marker not in ("assessment_placeholder_allowed",):
            issues.append(f"placeholder_or_unresolved:{marker}")
    required_parts = [f"part_{i:02d}" for i in range(1, 12)]
    for p in required_parts:
        if p not in report:
            issues.append(f"missing_{p}")
    quality = 100.0 if not issues else max(0.0, 100 - 5 * len(issues))
    evidence_ready = evidence_count > 0 or report.get("context", {}).get("evidence_required") is False
    release_ready = quality >= QUALITY_TARGET and not issues and evidence_ready
    return {"quality": quality, "release_ready": release_ready, "issues": issues, "evidence_ready": evidence_ready, "timestamp": now(), "spec_version": SPEC_VERSION}


def build_strict_runtime(text: str, evidence_count: int = 0) -> dict[str, Any]:
    p = classification(text)
    report = {
        "spec_version": SPEC_VERSION,
        "profile": p,
        "part_01": {"role": "PROMBARJIN Ω Enterprise X", "objectives": PRIORITIES, "profile": p, "absolute_rules": ["never fabricate", "never invent sources", "explicit assumptions", "FACT/INFERENCE/ESTIMATE/OPINION/SPECULATION separation"], "supported_domains": DOMAINS, "output_modes": OUTPUT_MODES, "self_validation": ["logical", "numerical", "timeline", "terminology", "units", "entity", "duplication", "contradiction"], "quality_target": QUALITY_TARGET},
        "part_02": {"problem": problem_model(text, p), "first_order": first_order(text), "second_order": second_order(), "third_order": third_order(), "system_thinking": system_map(), "root_cause": root_cause(text), "counterfactuals": counterfactuals(), "hypotheses": hypotheses(text), "assumption_audit": assumptions(text), "bias_firewall": bias_firewall(text), "information_asymmetry": information_asymmetry(), "decision_impact": decision_impact(), "uncertainty": {"confidence": None, "evidence_strength": None, "unknown_variables": [], "confidence_drivers": [], "confidence_reducers": []}, "executive_summary": {"key_findings": [], "critical_risks": [], "recommended_decision": None, "next_actions": [], "confidence_score": None}},
        "part_03": research_runtime(),
        "part_04": decision_runtime(),
        "part_05": financial_runtime(),
        "part_06": mining_runtime(),
        "part_07": energy_runtime(),
        "part_08": memory_runtime(),
        "part_09": governance_runtime(),
        "part_10": output_runtime(),
        "part_11": {"master_runtime": {"mission_detection": p["mission"], "task_classification": p, "domain_routing": p["primary_domain"], "execution_mode": p["required_depth"], "adaptive_depth": p["required_depth"], "pipeline": ["Mission Detection","Task Classification","Domain Routing","Research","Reasoning","Risk Analysis","Financial Analysis","Domain Analysis","Governance","Quality Gate","Output Compiler"], "conflict_resolution": ["Evidence","Logic","Freshness","Domain Authority","Consistency"], "fail_safe": ["increase research", "increase validation", "recalculate", "disclose uncertainty"]}},
        "context": {"evidence_required": p["evidence_requirement"] != "low", "evidence_count": evidence_count}
    }
    report["gate"] = strict_release_gate(report, evidence_count)
    return report
