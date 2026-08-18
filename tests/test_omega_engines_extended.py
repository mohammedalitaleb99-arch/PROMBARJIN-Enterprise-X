from app.omega_engines import (
    confidence_calibration, five_whys, fishbone, fault_tree, scenario_matrix,
    risk_register, validate_option_set, weighted_decision_matrix, npv, payback_period,
    sensitivity, unit_convert, mining_penalty_check, energy_value_chain, audit_item,
    executive_action_plan, information_lifecycle, master_pipeline,
)


def test_cognitive_and_root_cause_layers():
    assert len(five_whys('late shipment')) == 5
    assert set(fishbone('late shipment')) >= {'People', 'Process', 'Technology'}
    assert len(fault_tree('late shipment')['contributing_failures']) >= 4


def test_scenario_and_risk_engines():
    assert set(scenario_matrix('project')) == {'best_case','expected_case','worst_case','stress_case','black_swan_case'}
    risks = risk_register(['Strategic','Financial','Operational','Legal','Cyber','ESG'])
    assert len(risks) == 6 and all('residual_risk' in r for r in risks)


def test_decision_option_and_weighted_matrix():
    options = [{'name': f'o{i}', 'type': 'realistic'} for i in range(5)]
    options += [{'name':'u1','type':'unconventional'},{'name':'u2','type':'unconventional'},{'name':'d1','type':'disruptive'}]
    assert validate_option_set(options).ok
    weights = {'strategic_value':0.5,'financial_value':0.3,'execution_risk':0.2}
    ranked = weighted_decision_matrix([
        {'name':'A','strategic_value':90,'financial_value':80,'execution_risk':10,'confidence':90},
        {'name':'B','strategic_value':80,'financial_value':95,'execution_risk':20,'confidence':90},
    ], weights)
    assert ranked[0]['confidence_adjusted_score'] >= ranked[1]['confidence_adjusted_score']


def test_financial_math():
    assert round(npv(0.1, [-100, 60, 60]), 6) == round(4.13223140495867, 6)
    assert payback_period([-100, 30, 40, 50]) is not None
    assert sensitivity(100, [-0.1, 0, 0.1]) == [90.0,100,110.00000000000001]


def test_unit_and_domain_engines():
    assert round(unit_convert(1000, 'kg', 'MT'), 6) == 1
    penalty = mining_penalty_check({'As': 0.2, 'Zn': 1.1})
    assert 'As' in penalty['detected'] and penalty['commercial_impact_required']
    assert energy_value_chain('LNG terminal storage pipeline') == 'midstream'


def test_governance_audit_pipeline():
    assert information_lifecycle('A') and information_lifecycle('E')
    a = audit_item('FIND','EVID-1')
    assert a['id'].startswith('FIND-') and a['dependency'] == 'EVID-1'
    plan = executive_action_plan()
    assert set(plan) >= {'immediate_actions','30_day_plan','90_day_plan','long_term_roadmap','kpis','milestones'}
    pipe = master_pipeline('Research and decide whether to invest in an oil project')
    assert pipe['stages'][0] == 'mission_detection' and pipe['stages'][-1] == 'output_compiler'


def test_confidence_gate():
    assert confidence_calibration(100, 0, 0).ok
    assert not confidence_calibration(90, 0, 0).ok
