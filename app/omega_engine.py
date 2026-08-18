"""Executable PROMBARJIN OMEGA runtime primitives.

This module turns the OMEGA specification into enforceable programmatic gates.
It intentionally avoids hidden reasoning exposure: it stores structured metadata,
validation results, evidence requirements, decision options, risks, and audit IDs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
import re
from typing import Any, Iterable

PRIORITIES = {
    "truth": 1, "safety": 2, "accuracy": 3, "logical_consistency": 4,
    "evidence_quality": 5, "completeness": 6, "executive_utility": 7, "efficiency": 8,
}

DOMAINS = {
    "finance": {"finance", "accounting", "fp&a", "investment", "valuation", "npv", "irr", "forecast"},
    "mining": {"mining", "critical mineral", "antimony", "tin", "tungsten", "copper", "lithium", "nickel", "cobalt", "graphite", "rare earth", "ore", "concentrate", "jorc", "ni43-101", "samrec"},
    "energy": {"oil", "gas", "lng", "lpg", "refining", "petrochemical", "energy", "renewable", "hydrogen", "carbon", "ccus", "esg", "climate", "opec", "brent", "wti"},
    "negotiation": {"negotiation", "offtake", "procurement", "batna", "zopa", "joint venture", "contract renewal"},
    "research": {"research", "sources", "evidence", "verify", "literature", "market study"},
    "strategy": {"strategy", "competitive", "portfolio", "growth", "market entry", "scenario"},
    "coding": {"code", "coding", "software", "api", "python", "javascript", "bug", "repository"},
    "legal": {"legal", "regulation", "regulatory", "contract", "compliance", "arbitration", "law"},
    "engineering": {"engineering", "design", "process", "metallurgy", "pipeline", "plant", "failure"},
}

OUTPUT_MODES = {"executive brief", "technical report", "deep analysis", "decision memo", "academic style", "business proposal", "implementation plan", "step-by-step guide", "comparative matrix"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str, n: int = 0) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{n}"


@dataclass
class TaskProfile:
    primary_domain: str
    secondary_domains: list[str]
    complexity: str
    urgency: str
    decision_risk: str
    evidence_requirement: str
    required_depth: str
    expected_output: str
    mission: str
    decision_type: str


@dataclass
class EvidenceItem:
    evidence_id: str
    claim: str
    source: str = ""
    level: str = "C"
    quality: str = "Unknown"
    freshness: str = "Unknown"
    independence: str = "Unknown"
    replication: str = "Unknown"
    confidence: float = 0.0
    status: str = "unverified"


@dataclass
class RiskItem:
    risk_id: str
    category: str
    description: str
    probability: float
    impact: float
    detectability: float
    mitigation: str
    residual_risk: float


@dataclass
class OptionScore:
    name: str
    strategic_value: float
    financial_value: float
    operational_complexity: float
    implementation_time: float
    capital_requirement: float
    execution_risk: float
    scalability: float
    resilience: float
    roi: float
    npv: float
    confidence: float
    weighted_score: float = 0.0
    risk_adjusted_score: float = 0.0
    confidence_adjusted_score: float = 0.0


@dataclass
class AuditTrail:
    finding_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    decision_ids: list[str] = field(default_factory=list)
    assumption_ids: list[str] = field(default_factory=list)
    calculation_ids: list[str] = field(default_factory=list)
    risk_ids: list[str] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    score: float
    logical_integrity: bool
    evidence_integrity: bool
    numerical_integrity: bool
    executive_integrity: bool
    governance_integrity: bool
    issues: list[str]

    @property
    def release_ready(self) -> bool:
        return (
            self.score >= 95
            and self.logical_integrity
            and self.evidence_integrity
            and self.numerical_integrity
            and self.executive_integrity
            and self.governance_integrity
        )


def classify_request(text: str) -> TaskProfile:
    t = text.lower()
    scores = {d: sum(1 for term in terms if term in t) for d, terms in DOMAINS.items()}
    active = [d for d, score in sorted(scores.items(), key=lambda x: x[1], reverse=True) if score > 0]
    primary = active[0] if active else "general"
    secondary = active[1:5]
    mission = "decision" if any(x in t for x in ("should we", "recommend", "decide", "decision", "choose")) else ("research" if any(x in t for x in ("research", "analyze", "investigate", "sources")) else "analysis")
    complexity = "high" if len(text) >= 1200 or len(active) >= 3 else ("medium" if len(text) >= 500 or active else "low")
    urgency = "high" if any(x in t for x in ("urgent", "immediately", "today", "deadline", "critical")) else "normal"
    risk = "high" if any(x in t for x in ("legal", "investment", "regulatory", "safety", "contract", "compliance")) else ("medium" if active else "low")
    evidence = "high" if mission in {"research", "decision"} or risk == "high" else "medium"
    depth = "maximum precision" if risk == "high" else ("deep" if complexity == "high" else "balanced")
    expected = next((m.title() for m in OUTPUT_MODES if m in t), "Executive Brief")
    decision_type = "strategic" if any(x in t for x in ("strategy", "portfolio", "investment", "market entry")) else mission
    return TaskProfile(primary, secondary, complexity, urgency, risk, evidence, depth, expected, mission, decision_type)


def generate_alternative_hypotheses(problem: str) -> list[str]:
    base = problem.strip() or "the observed outcome"
    return [
        f"Primary explanation: the most direct causal mechanism for {base}.",
        f"Alternative A: an external or environmental factor explains {base}.",
        f"Alternative B: a measurement, data-quality, or definition issue explains {base}.",
        f"Alternative C: an incentive, behavioral, or strategic response explains {base}.",
    ]


def five_whys(problem: str) -> list[str]:
    if not problem.strip():
        return []
    return [f"Why {i}? Investigate the causal layer behind the prior answer." for i in range(1, 6)]


def build_scenarios(topic: str) -> dict[str, str]:
    return {
        "best_case": f"Favorable assumptions and reinforcing conditions for {topic}.",
        "expected_case": f"Base-rate outcome using currently supported evidence for {topic}.",
        "worst_case": f"Major adverse conditions materialize for {topic}.",
        "stress_case": f"Multiple adverse drivers combine and test the decision for {topic}.",
        "black_swan_case": f"Low-probability, high-impact discontinuity affecting {topic}.",
    }


def weighted_option_score(option: OptionScore, weights: dict[str, float] | None = None) -> OptionScore:
    w = weights or {
        "strategic_value": 0.14, "financial_value": 0.14, "operational_complexity": 0.08,
        "implementation_time": 0.08, "capital_requirement": 0.08, "execution_risk": 0.12,
        "scalability": 0.09, "resilience": 0.09, "roi": 0.09, "npv": 0.05, "confidence": 0.04,
    }
    # All scores are normalized 0..100; higher is better. Cost/risk dimensions are inverted.
    positive = (
        option.strategic_value * w["strategic_value"]
        + option.financial_value * w["financial_value"]
        + (100 - option.operational_complexity) * w["operational_complexity"]
        + (100 - option.implementation_time) * w["implementation_time"]
        + (100 - option.capital_requirement) * w["capital_requirement"]
        + (100 - option.execution_risk) * w["execution_risk"]
        + option.scalability * w["scalability"]
        + option.resilience * w["resilience"]
        + option.roi * w["roi"]
        + option.npv * w["npv"]
        + option.confidence * w["confidence"]
    )
    option.weighted_score = positive
    option.risk_adjusted_score = positive * (1 - option.execution_risk / 200)
    option.confidence_adjusted_score = option.risk_adjusted_score * (0.5 + option.confidence / 200)
    return option


def numeric_consistency(values: Iterable[float]) -> tuple[bool, str]:
    vals = list(values)
    if any(not isinstance(x, (int, float)) or not math.isfinite(float(x)) for x in vals):
        return False, "non_finite_number"
    return True, "ok"


def detect_assumptions(text: str) -> list[dict[str, Any]]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    candidates = [s for s in sentences if any(k in s.lower() for k in ("assume", "assuming", "likely", "may", "might", "could", "expected"))]
    return [{"assumption_id": _id("ASM", i), "text": s, "confidence": 50, "evidence": "needs validation"} for i, s in enumerate(candidates)]


def route_engines(profile: TaskProfile) -> list[str]:
    engines = {"kernel", "governance", "memory", "output"}
    if profile.mission == "research" or profile.evidence_requirement == "high":
        engines.add("research")
    if profile.mission == "decision":
        engines.add("decision")
        engines.add("risk")
    if profile.primary_domain == "finance" or "finance" in profile.secondary_domains:
        engines.add("finance")
    if profile.primary_domain == "mining" or "mining" in profile.secondary_domains:
        engines.add("mining")
    if profile.primary_domain == "energy" or "energy" in profile.secondary_domains:
        engines.add("energy")
    if profile.primary_domain == "negotiation":
        engines.add("negotiation")
    if profile.primary_domain == "coding":
        engines.add("coding")
    if profile.primary_domain == "legal":
        engines.add("legal")
    return sorted(engines)


def final_quality_gate(*, answer: str, profile: TaskProfile, evidence: list[EvidenceItem], risks: list[RiskItem], audit: AuditTrail, contradictions: list[str] | None = None) -> QualityReport:
    issues: list[str] = []
    if not answer.strip():
        issues.append("empty_output")
    if profile.evidence_requirement == "high" and not evidence:
        issues.append("missing_evidence_for_high_requirement")
    if not audit.validations:
        issues.append("missing_audit_validations")
    if contradictions:
        issues.extend(f"unresolved_contradiction:{x}" for x in contradictions)
    numerical_ok, numerical_issue = numeric_consistency([r.residual_risk for r in risks])
    if not numerical_ok:
        issues.append(numerical_issue)
    # Governance checks are hard gates; the answer is not released merely because it is non-empty.
    logical = not any("contradiction" in x for x in issues)
    evidence_ok = profile.evidence_requirement != "high" or bool(evidence)
    executive = any(k in answer.lower() for k in ("key findings", "recommend", "next actions", "confidence"))
    governance = not any(x.startswith("missing_") for x in issues)
    score = max(0.0, 100.0 - min(100.0, 10.0 * len(issues)))
    return QualityReport(score, logical, evidence_ok, numerical_ok, executive, governance, issues)


def build_runtime_context(text: str) -> dict[str, Any]:
    profile = classify_request(text)
    hypotheses = generate_alternative_hypotheses(text)
    assumptions = detect_assumptions(text)
    audit = AuditTrail()
    audit.assumption_ids.extend(a["assumption_id"] for a in assumptions)
    audit.validations.extend(["mission_detected", "task_classified", "domain_routed", "uncertainty_flagged"])
    return {
        "profile": profile,
        "engines": route_engines(profile),
        "hypotheses": hypotheses,
        "five_whys": five_whys(text),
        "scenarios": build_scenarios(text),
        "assumptions": assumptions,
        "audit": audit,
        "priority_order": PRIORITIES,
    }
