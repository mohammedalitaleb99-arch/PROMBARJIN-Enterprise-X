from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Any, Iterable

@dataclass
class ValidationResult:
    ok: bool
    score: float
    issues: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def confidence_calibration(evidence_strength: float, unknowns: int = 0, contradictions: int = 0) -> ValidationResult:
    score = max(0.0, min(100.0, evidence_strength - unknowns * 5 - contradictions * 10))
    issues = []
    if contradictions: issues.append("unresolved_contradictions")
    if unknowns: issues.append("critical_unknowns_present")
    return ValidationResult(score >= 95, score, issues)


def five_whys(problem: str) -> list[str]:
    return [f"Why {i}? Investigate the causal layer behind: {problem}" for i in range(1, 6)] if problem.strip() else []


def fishbone(problem: str) -> dict[str, str]:
    return {k: f"Potential {k.lower()} causes for {problem}" for k in ["People", "Process", "Technology", "Materials", "Measurement", "Environment"]}


def fault_tree(problem: str) -> dict[str, list[str]]:
    return {"top_event": problem, "contributing_failures": ["people_failure", "process_failure", "technology_failure", "external_failure"]}


def constraint_analysis(constraints: Iterable[str]) -> list[dict[str, Any]]:
    return [{"constraint": c, "impact": "assess", "mitigation": "define"} for c in constraints]


def scenario_matrix(topic: str) -> dict[str, dict[str, Any]]:
    return {s: {"topic": topic, "financial": "assess", "operational": "assess", "strategic": "assess", "recovery": "assess"}
            for s in ["best_case", "expected_case", "worst_case", "stress_case", "black_swan_case"]}


def risk_register(categories: Iterable[str]) -> list[dict[str, Any]]:
    out = []
    for i, c in enumerate(categories):
        out.append({"risk_id": f"RISK-{i+1}", "category": c, "probability": 0.5, "impact": 0.5,
                    "detectability": 0.5, "mitigation": "define", "residual_risk": 0.25})
    return out


def validate_option_set(options: list[dict[str, Any]]) -> ValidationResult:
    if len(options) < 8:
        return ValidationResult(False, len(options) / 8 * 100, ["minimum_8_options_required"])
    unconventional = sum(1 for o in options if o.get("type") == "unconventional")
    disruptive = sum(1 for o in options if o.get("type") == "disruptive")
    issues=[]
    if unconventional < 2: issues.append("minimum_2_unconventional_options_required")
    if disruptive < 1: issues.append("minimum_1_disruptive_option_required")
    return ValidationResult(not issues, 100 if not issues else 80, issues)


def weighted_decision_matrix(options: list[dict[str, float]], weights: dict[str, float]) -> list[dict[str, float]]:
    if not options: return []
    if abs(sum(weights.values()) - 1.0) > 1e-6: raise ValueError("weights_must_sum_to_1")
    result=[]
    for opt in options:
        weighted=sum(opt.get(k, 0.0) * w for k, w in weights.items())
        risk_adjusted=weighted * (1 - opt.get("execution_risk", 0.0)/100)
        confidence_adjusted=risk_adjusted * (opt.get("confidence", 0.0)/100)
        row=dict(opt); row.update(weighted_score=weighted, risk_adjusted_score=risk_adjusted, confidence_adjusted_score=confidence_adjusted)
        result.append(row)
    return sorted(result, key=lambda x: x["confidence_adjusted_score"], reverse=True)


def npv(rate: float, cash_flows: list[float]) -> float:
    if rate <= -1: raise ValueError("rate_must_be_greater_than_minus_100_percent")
    return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))


def payback_period(cash_flows: list[float]) -> float | None:
    cumulative = 0.0
    for i, cf in enumerate(cash_flows):
        prev = cumulative; cumulative += cf
        if cumulative >= 0 and prev < 0:
            return i - 1 + (-prev / cf if cf else 0)
    return None


def sensitivity(base_value: float, deltas: Iterable[float]) -> list[float]:
    return [base_value * (1 + d) for d in deltas]


def unit_convert(value: float, from_unit: str, to_unit: str) -> float:
    factors = {"kg": 1.0, "g": 0.001, "lb": 0.45359237, "oz": 0.028349523125, "ton": 1000.0, "MT": 1000.0, "DMT": 1000.0, "WMT": 1000.0}
    if from_unit not in factors or to_unit not in factors: raise ValueError("unsupported_unit")
    return value * factors[from_unit] / factors[to_unit]


def mining_penalty_check(elements: dict[str, float]) -> dict[str, Any]:
    penalty = [x for x in ["As","Hg","Pb","Cd","Bi","F","Cl","Se","Te","Cu","Zn","Fe","S"] if x in elements]
    return {"detected": penalty, "commercial_impact_required": bool(penalty)}


def energy_value_chain(sector_text: str) -> str:
    t = sector_text.lower()
    for name, keys in {"upstream":["exploration","production","reserve","lifting"], "midstream":["pipeline","terminal","storage","lng"], "downstream":["refining","petrochemical","retail"], "trading":["trading","merchant"]}.items():
        if any(k in t for k in keys): return name
    return "integrated_or_unspecified"


def audit_item(prefix: str, dependency: str = "") -> dict[str, str]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return {"id": f"{prefix}-{ts}", "timestamp": datetime.now(timezone.utc).isoformat(), "dependency": dependency, "status": "validated"}


def executive_action_plan() -> dict[str, Any]:
    return {"immediate_actions": [], "30_day_plan": [], "90_day_plan": [], "long_term_roadmap": [], "kpis": [], "milestones": []}


def information_lifecycle(level: str) -> bool:
    return level in {"A", "B", "C", "D", "E"}


def master_pipeline(request: str) -> dict[str, Any]:
    return {
        "stages": ["mission_detection", "task_classification", "domain_routing", "research", "reasoning", "risk_analysis", "financial_analysis", "domain_analysis", "governance", "quality_gate", "output_compiler"],
        "status": "ready",
        "request": request,
        "audit": audit_item("PIPE"),
    }
