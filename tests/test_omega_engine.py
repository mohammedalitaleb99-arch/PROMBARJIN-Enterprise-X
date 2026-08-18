from app.omega_engine import (
    build_runtime_context,
    classify_request,
    final_quality_gate,
    generate_alternative_hypotheses,
    weighted_option_score,
    OptionScore,
)


def test_classification_captures_required_metadata():
    p = classify_request('Analyze an oil and gas investment decision with NPV, risk and evidence requirements.')
    assert p.primary_domain == 'finance'
    assert p.decision_risk in {'high', 'medium'}
    assert p.evidence_requirement in {'high', 'medium'}
    assert p.required_depth in {'maximum precision', 'deep', 'balanced'}


def test_hypothesis_engine_has_at_least_three_alternatives():
    assert len(generate_alternative_hypotheses('market decline')) >= 3


def test_weighted_decision_scoring_is_calculated():
    option = OptionScore('A', 90, 80, 20, 20, 30, 20, 80, 85, 75, 70, 90)
    result = weighted_option_score(option)
    assert result.weighted_score > 0
    assert 0 <= result.risk_adjusted_score <= 100
    assert 0 <= result.confidence_adjusted_score <= 100


def test_runtime_routes_required_engines_for_financial_decision():
    runtime = build_runtime_context('Should we invest in a mining project? Analyze NPV, risks and market evidence.')
    assert 'kernel' in runtime['engines']
    assert 'decision' in runtime['engines']
    assert 'finance' in runtime['engines']
    assert 'mining' in runtime['engines']
    assert 'governance' in runtime['engines']
    assert len(runtime['hypotheses']) >= 3
    assert len(runtime['five_whys']) == 5


def test_release_gate_rejects_high_evidence_request_without_evidence():
    runtime = build_runtime_context('Research the current regulatory risk and recommend a decision.')
    gate = final_quality_gate(
        answer='Key Findings\nRecommendation\nNext Actions\nConfidence',
        profile=runtime['profile'],
        evidence=[],
        risks=[],
        audit=runtime['audit'],
    )
    assert gate.release_ready is False
    assert 'missing_evidence_for_high_requirement' in gate.issues
