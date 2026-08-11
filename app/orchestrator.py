from dataclasses import dataclass
from typing import List

DOMAINS = {
    'finance': {'finance','accounting','fp&a','investment','valuation','cash flow','npv','irr','forecast'},
    'mining': {'mining','antimony','tin','tungsten','copper','lithium','nickel','cobalt','graphite','rare earth','ore','concentrate'},
    'energy': {'oil','gas','lng','lpg','refining','petrochemical','energy','renewable','hydrogen','carbon','ccus','esg','climate'},
    'negotiation': {'negotiation','offtake','procurement','salary','joint venture','contract renewal','batna','zopa'},
    'career': {'cv','resume','linkedin','interview','career','job','certification'},
    'research': {'research','sources','evidence','verify','literature','market study'},
    'coding': {'code','coding','software','api','python','javascript','bug','repository'},
}

@dataclass
class TaskProfile:
    primary_domain: str
    secondary_domains: List[str]
    complexity: str
    urgency: str = 'normal'
    risk: str = 'medium'
    evidence_required: bool = True


def classify(text: str) -> TaskProfile:
    t = text.lower()
    scores = {d: sum(1 for term in terms if term in t) for d, terms in DOMAINS.items()}
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    active = [d for d, s in ranked if s > 0]
    primary = active[0] if active else 'general'
    secondary = active[1:4]
    complexity = 'high' if len(text) > 1200 or len(active) >= 3 else ('medium' if len(text) > 500 or active else 'low')
    risk = 'high' if any(w in t for w in ['legal','investment','contract','regulatory','safety']) else 'medium'
    return TaskProfile(primary, secondary, complexity, risk=risk, evidence_required=True)


def quality_gate(answer: str) -> dict:
    issues = []
    if not answer.strip(): issues.append('empty_output')
    if 'I am certain' in answer and 'evidence' not in answer.lower(): issues.append('unsupported_certainty')
    score = max(0, 100 - 20*len(issues))
    return {'status': 'PASS' if not issues else 'FAIL', 'score': score, 'issues': issues}


def system_context(profile: TaskProfile) -> str:
    return (
        'PROMBARJIN OMEGA runtime. Priorities: truth, safety, accuracy, logical consistency, '
        'evidence quality, completeness, executive utility, efficiency. Separate fact/inference/estimate/opinion/speculation. '
        f'Primary domain={profile.primary_domain}; secondary={", ".join(profile.secondary_domains) or "none"}; complexity={profile.complexity}. '
        'Use research when current external information is required. Never fabricate citations or live data.'
    )
