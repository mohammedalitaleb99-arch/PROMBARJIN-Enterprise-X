from datetime import datetime, timezone, timedelta

from app.omega_compliance import (
    QUALITY_TARGET, Evidence, Finding, AuditTrail, Risk,
    classify_request, five_whys, fishbone, fault_tree, counterfactuals,
    alternative_hypotheses, assumption_audit, bias_firewall, research_plan,
    source_credibility, freshness_validation, evidence_weight, contradiction_detector,
    citation_graph, red_team_review, confidence_calibration, option_requirements,
    weighted_decision_matrix, risk_engine, npv, irr, modified_irr, payback_period,
    ratio_engine, valuation_dcf, financial_stress, mining_penalties,
    validate_resource_classes, unit_consistency, energy_market, esg_assessment,
    sustainability_reporting, memory_context, decision_ledger_entry,
    governance_check, quality_score, action_engine, deliverable_check, master_runtime,
)


def test_kernel_classification_and_priorities():
    p = classify_request('Should we make an oil & gas investment decision under regulatory risk with evidence and a board memo?')
    assert p['primary_domain'] in {'finance', 'oil & gas'}
    assert p['decision_risk'] == 'high'
    assert p['evidence_requirement'] == 'high'
    assert p['required_depth'] == 'maximum precision'
    assert p['expected_output'] == 'decision memo'


def test_cognitive_engine_complete():
    assert len(five_whys('root failure')) == 5
    assert set(fishbone('root failure')) == {'People','Process','Technology','Materials','Measurement','Environment'}
    assert 'top_event' in fault_tree('root failure')
    cf = counterfactuals('decision'); assert set(cf) == {'scenario_a','scenario_b','scenario_c','best_case','worst_case','most_likely_case'}
    assert len(alternative_hypotheses('decision')) >= 4
    assert isinstance(assumption_audit('Assume demand remains stable.'), list)
    assert len(bias_firewall('confirmation bias')) == 8


def test_research_engine_controls():
    plan = research_plan('current regulatory risk'); assert plan['evidence_threshold'] == QUALITY_TARGET
    e = Evidence('E1','claim','official', 'A', 95,95,95,95,95,5,95, 'independent','replicated','verified')
    assert source_credibility(e) == 'Very High'
    fresh = freshness_validation(datetime.now(timezone.utc)-timedelta(days=2), None)
    assert fresh['freshness'] == 'current'
    assert evidence_weight(e)['strength'] == 'Strong'
    assert contradiction_detector([{'entity':'A','metric':'price','value':1},{'entity':'A','metric':'price','value':2}])
    assert citation_graph(['claim'], [e])[0]['evidence_ids'] == ['E1']
    assert isinstance(red_team_review('claim'), dict)
    assert confidence_calibration([95])['confidence_pct'] == 95


def test_decision_engine_requirements_and_matrix():
    options = [{'type':'realistic'} for _ in range(5)] + [{'type':'unconventional'} for _ in range(2)] + [{'type':'disruptive'}]
    assert option_requirements(options)
    scores = weighted_decision_matrix([
        {'name':'A','strategic':90,'financial':80,'execution_risk':20,'confidence':90},
        {'name':'B','strategic':80,'financial':85,'execution_risk':10,'confidence':80},
    ], {'strategic':0.4,'financial':0.4,'execution_risk':0.1,'confidence':0.1})
    assert scores[0]['confidence_adjusted_score'] >= 0
    risks = risk_engine(['strategic','financial','cyber'])
    assert len(risks) == 3


def test_financial_engine():
    flows=[-100,40,40,40,40]
    assert npv(.1, flows) > 0
    assert irr(flows) is not None
    assert modified_irr(flows,.1,.1) is not None
    assert payback_period(flows) is not None
    ratios=ratio_engine({'revenue':1000,'gross_profit':400,'ebitda':250,'operating_income':200,'net_income':100,'assets':1500,'equity':800,'debt':700,'cash':200,'current_assets':500,'current_liabilities':250,'inventory':100,'interest_expense':50,'cogs':600,'receivables':100,'payables':90})
    assert ratios['current_ratio'] == 2.0
    assert valuation_dcf([30,35,40],.10,.02) > 0
    assert len(financial_stress(flows,[-.2,0,.2])) == 3


def test_mining_engine():
    penalties=mining_penalties({'As':1.2,'Fe':2.0}); assert penalties['commercial_impact']
    resource=validate_resource_classes({'measured':10,'indicated':20,'jorc_compliance':True,'data_confidence':90})
    assert 'measured' in resource['present']
    assert unit_consistency(['ppm','g/t','MT'])


def test_energy_esg_engine():
    m=energy_market({'brent':80,'wti':75,'supply':10,'demand':11}); assert m['commodity_prices']['brent'] == 80
    e=esg_assessment({'methane':'high','water_risk':'medium'}); assert e['methane'] == 'high'
    s=sustainability_reporting({'IFRS S1':'supported','ISSB':'supported'}); assert s['IFRS S1'] == 'supported'


def test_memory_governance_output_and_master_runtime():
    mem=memory_context(); assert mem['priority'][0] == 'user_objective'
    ledger=decision_ledger_entry('Buy','Evidence supports',95); assert ledger['decision_id'].startswith('DEC-')
    audit=AuditTrail(validation_status=['mission_detection','task_classification','domain_routing','governance'])
    finding=Finding('F1','claim','FACT',98)
    evidence=Evidence('E1','claim','official','A',95,95,95,95,95,5,95,'independent','replicated','verified')
    gate=governance_check([finding],[evidence],[],audit,[],True,True,'Key Findings\nRecommendation\nConfidence')
    assert gate.quality >= 95 or not gate.release_ready
    metrics={k:100 for k in ['accuracy','evidence','depth','reasoning','consistency','completeness','executive_value','actionability','traceability']}
    assert quality_score(metrics) == 100
    assert set(action_engine()) == {'immediate_actions','30_day_plan','90_day_plan','long_term_roadmap','kpis','milestones'}
    assert deliverable_check('recommendation\nconfidence\nnext actions')['decision_readiness']
    runtime=master_runtime('Research an oil and gas investment decision under regulatory risk.')
    assert runtime['mission'] == 'research'
    assert 'governance' in runtime['engines']
    assert runtime['execution_mode'] == 'maximum precision'
