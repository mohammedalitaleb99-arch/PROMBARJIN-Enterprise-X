from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Iterable

SPEC_VERSION = "1.0"
QUALITY_TARGET = 95.0

PRIORITIES = ["truth", "safety", "accuracy", "logical_consistency", "evidence_quality", "completeness", "executive_utility", "efficiency"]

DOMAINS = [
    "finance", "corporate finance", "fp&a", "investment", "accounting", "mining", "critical minerals", "antimony",
    "oil & gas", "commodity trading", "supply chain", "economics", "strategy", "esg", "risk", "negotiation",
    "research", "writing", "coding", "legal analysis", "scientific analysis", "engineering"
]

OUTPUT_MODES = ["executive brief", "technical report", "deep analysis", "decision memo", "academic style", "business proposal", "implementation plan", "step-by-step guide", "comparative matrix"]

BIAS_TYPES = ["confirmation bias", "anchoring", "availability bias", "authority bias", "survivorship bias", "recency bias", "optimism bias", "groupthink"]

RISK_TYPES = ["strategic", "financial", "operational", "legal", "compliance", "technology", "supply", "geopolitical", "cyber", "esg"]

PENALTY_ELEMENTS = ["As", "Hg", "Pb", "Cd", "Bi", "F", "Cl", "Se", "Te", "Cu", "Zn", "Fe", "S"]

MINING_UNITS = ["%", "ppm", "g/t", "kg/t", "MT", "DMT", "WMT", "lb", "ton", "oz"]

ENERGY_FRAMEWORKS = ["IFRS S1", "IFRS S2", "GRI", "SASB", "TCFD", "ISSB", "CSRD", "GHG Protocol", "CDP", "UN SDGs"]

@dataclass
class Finding:
    finding_id: str
    claim: str
    classification: str
    confidence: float

@dataclass
class Evidence:
    evidence_id: str
    claim: str
    source: str
    level: str
    authority: float
    accuracy: float
    freshness: float
    transparency: float
    evidence: float
    bias_risk: float
    replicability: float
    independence: str = "unknown"
    replication: str = "unknown"
    verification_status: str = "unverified"

@dataclass
class Assumption:
    assumption_id: str
    text: str
    confidence: float
    evidence: str
    verification_method: str

@dataclass
class Risk:
    risk_id: str
    category: str
    probability: float
    impact: float
    detectability: float
    mitigation: str
    residual_risk: float

@dataclass
class AuditTrail:
    finding_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    decision_ids: list[str] = field(default_factory=list)
    assumption_ids: list[str] = field(default_factory=list)
    calculation_ids: list[str] = field(default_factory=list)
    risk_ids: list[str] = field(default_factory=list)
    validation_status: list[str] = field(default_factory=list)
    dependency_chain: list[str] = field(default_factory=list)

@dataclass
class ReleaseGate:
    quality: float
    logical_integrity: bool
    evidence_integrity: bool
    numerical_integrity: bool
    executive_integrity: bool
    governance_integrity: bool
    decision_ready: bool
    all_engines_pass: bool
    issues: list[str] = field(default_factory=list)

    @property
    def release_ready(self) -> bool:
        return self.quality >= QUALITY_TARGET and all([
            self.logical_integrity, self.evidence_integrity, self.numerical_integrity,
            self.executive_integrity, self.governance_integrity, self.decision_ready,
            self.all_engines_pass
        ])

def _id(prefix: str, n: int = 0) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{now}-{n}"

def priority_order() -> dict[str, int]:
    return {name: i + 1 for i, name in enumerate(PRIORITIES)}

def classify_request(text: str) -> dict[str, Any]:
    t = text.lower()
    matched = [d for d in DOMAINS if d in t]
    primary = matched[0] if matched else "general"
    secondary = matched[1:5]
    complexity = "high" if len(text) > 1200 or len(matched) >= 3 else ("medium" if len(text) > 500 or matched else "low")
    urgency = "high" if any(x in t for x in ["urgent", "immediately", "today", "deadline", "critical"]) else "normal"
    decision_risk = "high" if any(x in t for x in ["legal", "investment", "regulatory", "safety", "contract", "compliance", "high risk"]) else ("medium" if matched else "low")
    evidence_requirement = "high" if decision_risk == "high" or any(x in t for x in ["research", "sources", "evidence", "verify"]) else "medium"
    required_depth = "maximum precision" if decision_risk == "high" else ("deep" if complexity == "high" else "balanced")
    expected = next((m for m in OUTPUT_MODES if m in t), "executive brief")
    mission = "decision" if any(x in t for x in ["should we", "recommend", "decide", "decision", "choose"]) else ("research" if any(x in t for x in ["research", "investigate", "sources"]) else "analysis")
    return {"primary_domain": primary, "secondary_domains": secondary, "complexity": complexity, "urgency": urgency, "decision_risk": decision_risk, "evidence_requirement": evidence_requirement, "required_depth": required_depth, "expected_output": expected, "mission": mission}

def identify_problem(text: str) -> dict[str, Any]:
    return {"problem": text.strip(), "goal": "Produce a verified, decision-useful result", "desired_outcome": "Decision-ready deliverable", "constraints": [], "unknown_variables": [], "stakeholders": [], "risk_level": classify_request(text)["decision_risk"], "decision_type": classify_request(text)["mission"]}

def first_order(text: str) -> dict[str, list[str]]:
    return {"immediate_effects": [f"Direct effects of {text}"], "direct_consequences": [f"Immediate consequences of {text}"], "expected_benefits": ["Identify measurable benefits"], "expected_costs": ["Identify measurable costs"]}

def second_order(text: str) -> dict[str, list[str]]:
    return {"indirect_effects": ["Map indirect effects"], "delayed_effects": ["Map delayed effects"], "hidden_tradeoffs": ["Identify hidden tradeoffs"], "opportunity_cost": ["Quantify opportunity cost where data permit"], "feedback_loops": ["Identify feedback loops"]}

def third_order(text: str) -> dict[str, list[str]]:
    return {"long_term_impact": ["Assess long-term impact"], "strategic_consequences": ["Assess strategic consequences"], "behavioral_reactions": ["Assess stakeholder and behavioral reactions"], "market_reactions": ["Assess market response"], "system_dynamics": ["Map system dynamics"]}

def system_map() -> dict[str, list[str]]:
    return {k: [] for k in ["inputs", "processes", "dependencies", "constraints", "outputs", "feedback", "failure_points"]}

def five_whys(problem: str) -> list[str]:
    if not problem.strip(): return []
    return [f"Why {i}: identify the next causal layer for {problem}" for i in range(1, 6)]

def fishbone(problem: str) -> dict[str, list[str]]:
    causes = ["People", "Process", "Technology", "Materials", "Measurement", "Environment"]
    return {c: [f"Investigate {c} contributors"] for c in causes}

def fault_tree(problem: str) -> dict[str, Any]:
    return {"top_event": problem, "gates": {"OR": ["people failure", "process failure", "technology failure", "external failure"]}}

def constraint_analysis(constraints: Iterable[str]) -> list[dict[str, Any]]:
    return [{"constraint": c, "binding": None, "impact": None, "mitigation": None} for c in constraints]

def counterfactuals(text: str) -> dict[str, str]:
    return {"scenario_a": f"What if the key assumption improves for {text}?", "scenario_b": f"What if the key assumption worsens for {text}?", "scenario_c": f"What if the key assumption reverses for {text}?", "best_case": "Most favorable supported outcome", "worst_case": "Most adverse supported outcome", "most_likely_case": "Base-rate supported outcome"}

def alternative_hypotheses(text: str) -> list[str]:
    return [f"Primary explanation for {text}", f"Alternative A: external/environmental cause of {text}", f"Alternative B: data/measurement/definition issue in {text}", f"Alternative C: incentive/behavior/strategy cause of {text}"]

def assumption_audit(text: str) -> list[Assumption]:
    terms = [s.strip() for s in text.replace(";", ".").split(".") if s.strip()]
    candidates = [s for s in terms if any(k in s.lower() for k in ["assume", "assuming", "likely", "may", "might", "could", "expected"])]
    return [Assumption(_id("ASM", i), s, 50.0, "not yet verified", "identify source or calculate validation") for i, s in enumerate(candidates)]

def bias_firewall(text: str) -> list[dict[str, str]]:
    t = text.lower(); out=[]
    for b in BIAS_TYPES:
        hit = b in t
        out.append({"bias": b, "detected": str(hit), "action": "counter-test" if hit else "monitor"})
    return out

def information_asymmetry() -> dict[str, list[str]]:
    return {"missing_information": [], "unknown_unknowns": [], "blind_spots": [], "hidden_incentives": []}

def decision_impact() -> dict[str, Any]:
    return {"financial": None, "operational": None, "strategic": None, "reputation": None, "legal": None, "esg": None}

def uncertainty_engine(conclusions: Iterable[str], evidence: Iterable[Evidence]) -> list[dict[str, Any]]:
    ev = list(evidence); base = sum(x.confidence for x in ev) / len(ev) if ev else 0.0
    return [{"conclusion": c, "confidence": round(base, 2), "evidence_strength": "strong" if base >= 75 else "weak", "unknown_variables": [], "confidence_drivers": [], "confidence_reducers": []} for c in conclusions]

def executive_summary(findings: list[str], risks: list[str], decision: str, actions: list[str], confidence: float) -> dict[str, Any]:
    return {"key_findings": findings, "critical_risks": risks, "recommended_decision": decision, "next_actions": actions, "confidence_score": confidence}

def research_plan(question: str) -> dict[str, Any]:
    return {"primary_research_question": question, "secondary_questions": [], "known_facts": [], "unknown_facts": [], "critical_unknowns": [], "research_scope": "task-defined", "time_horizon": "task-defined", "evidence_threshold": QUALITY_TARGET}

def source_credibility(e: Evidence) -> str:
    avg = sum([e.authority, e.accuracy, e.freshness, e.transparency, e.evidence, 100-e.bias_risk, e.replicability]) / 7
    return "Very High" if avg >= 90 else "High" if avg >= 75 else "Medium" if avg >= 60 else "Low" if avg >= 40 else "Very Low"

def freshness_validation(publication_date: datetime | None, revision_date: datetime | None, current: datetime | None = None) -> dict[str, Any]:
    now = current or datetime.now(timezone.utc)
    latest = max([d for d in [publication_date, revision_date] if d], default=None)
    if latest is None: return {"valid": False, "reason": "no_date"}
    age_days = (now - latest).days
    return {"valid": True, "age_days": age_days, "freshness": "current" if age_days <= 30 else ("aging" if age_days <= 365 else "stale")}

def evidence_weight(e: Evidence) -> dict[str, Any]:
    score = (e.authority + e.accuracy + e.freshness + e.transparency + e.evidence + (100-e.bias_risk) + e.replicability) / 7
    strength = "Strong" if score >= 80 else "Moderate" if score >= 60 else "Weak" if score >= 40 else "Unsupported"
    return {"evidence_id": e.evidence_id, "strength": strength, "score": score, "type": e.level, "verification_status": e.verification_status, "consistency": e.independence, "replication": e.replication}

def contradiction_detector(claims: list[dict[str, Any]]) -> list[str]:
    conflicts=[]
    for i,a in enumerate(claims):
        for b in claims[i+1:]:
            if a.get("entity") == b.get("entity") and a.get("metric") == b.get("metric") and a.get("value") != b.get("value"):
                conflicts.append(f"conflict:{a.get('entity')}:{a.get('metric')}")
    return conflicts

def citation_graph(claims: Iterable[str], evidence: Iterable[Evidence]) -> list[dict[str, Any]]:
    ev=list(evidence)
    return [{"claim": c, "evidence_ids": [e.evidence_id for e in ev if e.claim == c], "confidence": max([e.confidence for e in ev if e.claim == c] or [0]), "dependency": []} for c in claims]

def knowledge_gaps() -> dict[str, list[str]]:
    return {"missing_variables": [], "missing_data": [], "missing_sources": [], "missing_calculations": [], "missing_assumptions": [], "recommended_information": []}

def red_team_review(text: str) -> dict[str, list[str]]:
    return {"weak_logic": [], "hidden_assumptions": [], "ignored_risks": [], "contradictory_evidence": [], "numerical_errors": [], "selection_bias": [], "confirmation_bias": []}

def confidence_calibration(evidence_scores: Iterable[float], limiting_factors: int = 0) -> dict[str, Any]:
    scores=list(evidence_scores); base=sum(scores)/len(scores) if scores else 0.0
    confidence=max(0.0, min(100.0, base - limiting_factors*5))
    return {"confidence_pct": confidence, "supporting_evidence": base, "limiting_factors": limiting_factors, "verification_status": "verified" if confidence >= QUALITY_TARGET else "insufficient", "required_next_step": "continue validation" if confidence < QUALITY_TARGET else "none"}

def decision_definition() -> dict[str, Any]:
    return {k: None for k in ["decision_owner", "decision_objective", "decision_horizon", "decision_constraints", "critical_success_factors", "failure_criteria", "reversibility", "cost_of_delay"]}

def option_requirements(options: list[dict[str, Any]]) -> bool:
    realistic=sum(1 for o in options if o.get("type") == "realistic")
    unconventional=sum(1 for o in options if o.get("type") == "unconventional")
    disruptive=sum(1 for o in options if o.get("type") == "disruptive")
    return realistic >= 5 and unconventional >= 2 and disruptive >= 1

def weighted_decision_matrix(options: list[dict[str, float]], weights: dict[str,float]) -> list[dict[str,float]]:
    if not options: return []
    if abs(sum(weights.values()) - 1) > 1e-6: raise ValueError("weights_must_sum_to_1")
    out=[]
    for o in options:
        weighted=sum(o.get(k,0)*w for k,w in weights.items())
        risk_adj=weighted*(1-o.get("execution_risk",0)/100)
        conf_adj=risk_adj*(o.get("confidence",0)/100)
        r=dict(o); r.update(weighted_score=weighted, risk_adjusted_score=risk_adj, confidence_adjusted_score=conf_adj); out.append(r)
    return sorted(out,key=lambda x:x["confidence_adjusted_score"],reverse=True)

def risk_engine(categories: Iterable[str]) -> list[Risk]:
    out=[]
    for i,c in enumerate(categories): out.append(Risk(_id("RISK",i), c, .5,.5,.5,"define mitigation from evidence",.25))
    return out

def npv(rate: float, cash_flows: list[float]) -> float:
    if rate <= -1: raise ValueError("rate_must_be_greater_than_minus_100_percent")
    return sum(cf/((1+rate)**i) for i,cf in enumerate(cash_flows))

def irr(cash_flows: list[float], low: float=-0.9999, high: float=10.0) -> float | None:
    if not any(cf < 0 for cf in cash_flows) or not any(cf > 0 for cf in cash_flows): return None
    for _ in range(200):
        mid=(low+high)/2; val=npv(mid,cash_flows)
        if abs(val)<1e-9: return mid
        if val>0: low=mid
        else: high=mid
    return (low+high)/2

def modified_irr(cash_flows: list[float], finance_rate: float, reinvest_rate: float) -> float | None:
    if len(cash_flows) < 2: return None
    n=len(cash_flows)-1; pv=sum(cf/((1+finance_rate)**i) for i,cf in enumerate(cash_flows) if cf < 0); fv=sum(cf*((1+reinvest_rate)**(n-i)) for i,cf in enumerate(cash_flows) if cf > 0)
    if pv == 0: return None
    return (fv/(-pv))**(1/n)-1

def payback_period(cash_flows:list[float]) -> float|None:
    cumulative=0.0
    for i,cf in enumerate(cash_flows):
        prev=cumulative; cumulative+=cf
        if prev<0<=cumulative and cf:
            return i-1+(-prev/cf)
    return None

def ratio_engine(data: dict[str,float]) -> dict[str,float|None]:
    revenue=data.get("revenue"); gross_profit=data.get("gross_profit"); ebitda=data.get("ebitda"); operating_income=data.get("operating_income"); net_income=data.get("net_income"); assets=data.get("assets"); equity=data.get("equity"); debt=data.get("debt"); cash=data.get("cash"); current_assets=data.get("current_assets"); current_liabilities=data.get("current_liabilities"); inventory=data.get("inventory"); interest=data.get("interest_expense"); cogs=data.get("cogs"); receivable=data.get("receivables"); payable=data.get("payables")
    return {"current_ratio": current_assets/current_liabilities if current_liabilities else None,"quick_ratio": (current_assets-inventory)/current_liabilities if current_liabilities else None,"cash_ratio": cash/current_liabilities if current_liabilities else None,"debt_ratio": debt/assets if assets else None,"debt_to_equity": debt/equity if equity else None,"interest_coverage": ebitda/interest if interest else None,"roa": net_income/assets if assets else None,"roe": net_income/equity if equity else None,"gross_margin": gross_profit/revenue if revenue else None,"operating_margin": operating_income/revenue if revenue else None,"net_margin": net_income/revenue if revenue else None,"asset_turnover": revenue/assets if assets else None,"inventory_turnover": cogs/inventory if inventory else None,"receivable_days": receivable/revenue*365 if revenue else None,"payable_days": payable/cogs*365 if cogs else None}

def valuation_dcf(cash_flows:list[float], discount_rate:float, terminal_growth:float=0.0) -> float:
    pv=npv(discount_rate,[0]+cash_flows)
    terminal=cash_flows[-1]*(1+terminal_growth)/(discount_rate-terminal_growth) if discount_rate>terminal_growth else 0.0
    return pv + terminal/((1+discount_rate)**len(cash_flows))

def financial_stress(cash_flows:list[float], shocks:Iterable[float]) -> list[dict[str,float]]:
    base=npv(.1,cash_flows)
    return [{"shock":s,"npv":base*(1+s)} for s in shocks]

def mining_domain(data:dict[str,Any]) -> dict[str,Any]:
    return {"commodity":data.get("commodity"),"deposit_type":data.get("deposit_type"),"ore_type":data.get("ore_type"),"country":data.get("country"),"mining_stage":data.get("mining_stage"),"processing_stage":data.get("processing_stage"),"trading_stage":data.get("trading_stage"),"head_grade":data.get("head_grade"),"recoverable_grade":data.get("recoverable_grade"),"payable_grade":data.get("payable_grade"),"recovery_pct":data.get("recovery_pct"),"moisture":data.get("moisture"),"density":data.get("density"),"particle_size":data.get("particle_size"),"liberation":data.get("liberation")}

def mining_penalties(elements:dict[str,float]) -> dict[str,Any]:
    detected={k:v for k,v in elements.items() if k in PENALTY_ELEMENTS}
    return {"detected":detected,"commercial_impact":bool(detected),"smelter_penalty_required":bool(detected),"environmental_risk_review":bool(detected),"contract_risk_review":bool(detected)}

def validate_resource_classes(resource:dict[str,Any]) -> dict[str,Any]:
    allowed={"measured","indicated","inferred","probable_reserve","proved_reserve"}; present={k for k,v in resource.items() if v is not None and k in allowed}; return {"present":sorted(present),"jorc_compliance":resource.get("jorc_compliance"),"ni43_101_compliance":resource.get("ni43_101_compliance"),"data_confidence":resource.get("data_confidence")}

def trading_terms(data:dict[str,Any]) -> dict[str,Any]:
    return {"incoterm":data.get("incoterm"),"container_or_bulk":data.get("shipment_mode"),"insurance":data.get("insurance"),"freight":data.get("freight"),"port_risk":data.get("port_risk"),"logistics_risk":data.get("logistics_risk"),"payability_pct":data.get("payability_pct"),"treatment_charges":data.get("treatment_charges"),"refining_charges":data.get("refining_charges"),"penalties":data.get("penalties"),"bonuses":data.get("bonuses")}

def unit_consistency(units:Iterable[str]) -> bool:
    return all(u in MINING_UNITS for u in units)

def energy_domain(data:dict[str,Any]) -> dict[str,Any]:
    return {"industry":data.get("industry"),"subsector":data.get("subsector"),"value_chain":data.get("value_chain"),"business_model":data.get("business_model"),"asset_type":data.get("asset_type"),"ownership_structure":data.get("ownership_structure"),"revenue_drivers":data.get("revenue_drivers",[]),"cost_drivers":data.get("cost_drivers",[])}

def energy_market(data:dict[str,Any]) -> dict[str,Any]:
    return {"supply":data.get("supply"),"demand":data.get("demand"),"inventories":data.get("inventories"),"opec_plus":data.get("opec_plus"),"geopolitics":data.get("geopolitics"),"shipping":data.get("shipping"),"freight":data.get("freight"),"weather":data.get("weather"),"seasonality":data.get("seasonality"),"strategic_reserves":data.get("strategic_reserves"),"commodity_prices":{k:data.get(k) for k in ["wti","brent","dubai","henry_hub","ttf","jkm","coal","electricity","carbon","hydrogen"]}}

def esg_assessment(data:dict[str,Any]) -> dict[str,Any]:
    return {k:data.get(k) for k in ["environmental","social","governance","materiality","climate_risk","water_risk","waste","tailings","methane","biodiversity","human_rights","community_impact","supply_chain","transition_risk","physical_risk","carbon_exposure","carbon_price","climate_scenario","decarbonization_pathway","net_zero_alignment"]}

def sustainability_reporting(data:dict[str,Any]) -> dict[str,Any]:
    return {framework: data.get(framework) for framework in ENERGY_FRAMEWORKS}

def memory_context() -> dict[str,Any]:
    return {"session": ["goal","completed_tasks","pending_tasks","open_questions","assumptions","constraints","user_preferences","executive_decisions","knowledge_acquired"],"hierarchy":["current_message","current_session","project_context","persistent_knowledge","executive_decision_history"],"priority":["user_objective","verified_facts","executive_decisions","critical_constraints","supporting_context"]}

def decision_ledger_entry(decision:str, reason:str, confidence:float) -> dict[str,Any]:
    return {"decision_id":_id("DEC"),"decision":decision,"reason":reason,"confidence":confidence,"timestamp":datetime.now(timezone.utc).isoformat(),"dependencies":[],"reversal_conditions":[]}

def governance_check(findings:list[Finding], evidence:list[Evidence], risks:list[Risk], audit:AuditTrail, contradictions:list[str], numeric_ok:bool, all_engines_pass:bool, answer:str) -> ReleaseGate:
    issues=[]
    if contradictions: issues += [f"unresolved_contradiction:{x}" for x in contradictions]
    if not evidence: issues.append("evidence_missing")
    if not audit.validation_status: issues.append("audit_validation_missing")
    if not numeric_ok: issues.append("numerical_integrity_failed")
    if not findings: issues.append("findings_missing")
    if not all_engines_pass: issues.append("engine_failure")
    executive_ok=all(x in answer.lower() for x in ["key findings","recommend","confidence"])
    if not executive_ok: issues.append("executive_structure_missing")
    score=max(0.0,100.0-10.0*len(issues))
    return ReleaseGate(score, not contradictions, bool(evidence), numeric_ok, executive_ok, not issues, bool(findings), all_engines_pass, issues)

def quality_score(metrics:dict[str,float]) -> float:
    keys=["accuracy","evidence","depth","reasoning","consistency","completeness","executive_value","actionability","traceability"]
    vals=[float(metrics.get(k,0)) for k in keys]
    return sum(vals)/len(vals)

def output_profile(text:str)->str:
    t=text.lower(); mapping=[("financial","financial"),("legal","legal"),("research","research"),("proposal","proposal"),("presentation","presentation"),("report","report"),("coding","coding"),("negotiation","negotiation"),("scientific","scientific"),("technical","technical"),("executive","executive"),("consulting","consulting"),("educational","educational")]
    return next((name for key,name in mapping if key in t),"executive")

def action_engine()->dict[str,list[Any]]:
    return {"immediate_actions":[],"30_day_plan":[],"90_day_plan":[],"long_term_roadmap":[],"kpis":[],"milestones":[]}

def deliverable_check(answer:str)->dict[str,bool]:
    t=answer.lower(); return {"formatting":True,"flow":True,"consistency":"contradiction" not in t,"terminology":True,"executive_readability":True,"decision_readiness":"recommend" in t,"implementation_readiness":"next actions" in t}

def master_runtime(text:str)->dict[str,Any]:
    profile=classify_request(text); problem=identify_problem(text); assumptions=assumption_audit(text); audit=AuditTrail(validation_status=["mission_detection","task_classification","domain_routing"]); audit.assumption_ids += [a.assumption_id for a in assumptions]
    return {"mission":profile["mission"],"profile":profile,"problem":problem,"engines":["kernel","research","decision","finance","mining","energy","risk","negotiation","writing","coding","governance","memory","output"],"execution_mode":"maximum precision" if profile["decision_risk"]=="high" else "balanced","adaptive_depth":profile["required_depth"],"audit":audit}
