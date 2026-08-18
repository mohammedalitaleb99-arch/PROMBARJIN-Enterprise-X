from __future__ import annotations

from typing import Any, Callable

from app.omega_strict import build_strict_runtime, QUALITY_TARGET, PLACEHOLDER_MARKERS
from app.omega_compliance import (
    npv, irr, modified_irr, payback_period, ratio_engine, valuation_dcf,
    mining_penalties, unit_consistency, mining_domain, trading_terms,
    energy_domain, energy_market, esg_assessment, sustainability_reporting,
    memory_context, decision_ledger_entry, quality_score,
)


def _path(root: dict[str, Any], dotted: str) -> Any:
    cur: Any = root
    for part in dotted.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise AssertionError(f'missing_required_path:{dotted}')
    return cur


def _nonempty(value: Any, label: str) -> bool:
    assert value not in (None, '', [], {}), f'empty_required_control:{label}'
    return True


def _contains_all(container: Any, required: list[str], label: str) -> bool:
    missing = [x for x in required if x not in container]
    assert not missing, f'missing_required_items:{label}:{missing}'
    return True


def _manifest() -> list[tuple[str, Callable[[dict[str, Any]], bool]]]:
    return [
        ('P01-01 role', lambda r: _nonempty(_path(r, 'part_01.role'), 'P01-01')),
        ('P01-02 priorities', lambda r: _contains_all(_path(r, 'part_01.objectives'), ['truth','safety','accuracy','logical_consistency','evidence_quality','completeness','executive_utility','efficiency'], 'P01-02')),
        ('P01-03 absolute rules', lambda r: _contains_all(_path(r, 'part_01.absolute_rules'), ['never fabricate','never invent sources','explicit assumptions','FACT/INFERENCE/ESTIMATE/OPINION/SPECULATION separation'], 'P01-03')),
        ('P01-04 supported domains', lambda r: len(_path(r, 'part_01.supported_domains')) >= 20),
        ('P01-05 output modes', lambda r: len(_path(r, 'part_01.output_modes')) >= 9),
        ('P01-06 self validation', lambda r: len(_path(r, 'part_01.self_validation')) >= 8),
        ('P01-07 quality target', lambda r: _path(r, 'part_01.quality_target') >= QUALITY_TARGET),
        ('P01-08 task classification', lambda r: _nonempty(_path(r, 'part_01.profile'), 'P01-08')),
        ('P01-09 primary domain', lambda r: _path(r, 'part_01.profile.primary_domain') in {'finance','oil & gas'}),
        ('P02-01 problem model', lambda r: _nonempty(_path(r, 'part_02.problem.problem'), 'P02-01')),
        ('P02-02 first order', lambda r: _contains_all(_path(r, 'part_02.first_order'), ['immediate_effects','direct_consequences','expected_benefits','expected_costs'], 'P02-02')),
        ('P02-03 second order', lambda r: _contains_all(_path(r, 'part_02.second_order'), ['indirect_effects','delayed_effects','hidden_tradeoffs','opportunity_cost','feedback_loops'], 'P02-03')),
        ('P02-04 third order', lambda r: _contains_all(_path(r, 'part_02.third_order'), ['long_term_impact','strategic_consequences','behavioral_reactions','market_reactions','system_dynamics'], 'P02-04')),
        ('P02-05 system thinking', lambda r: _contains_all(_path(r, 'part_02.system_thinking'), ['inputs','processes','dependencies','constraints','outputs','feedback','failure_points'], 'P02-05')),
        ('P02-06 root cause 5 whys', lambda r: len(_path(r, 'part_02.root_cause.five_whys')) == 5),
        ('P02-07 counterfactuals', lambda r: _contains_all(_path(r, 'part_02.counterfactuals'), ['scenario_a','scenario_b','scenario_c','best_case','worst_case','most_likely_case'], 'P02-07')),
        ('P02-08 hypotheses', lambda r: len(_path(r, 'part_02.hypotheses')) >= 3),
        ('P02-09 bias firewall', lambda r: len(_path(r, 'part_02.bias_firewall')) >= 8),
        ('P03-01 planning', lambda r: _contains_all(_path(r, 'part_03.planning'), ['primary_research_question','secondary_questions','known_facts','unknown_facts','critical_unknowns','research_scope','time_horizon','evidence_threshold'], 'P03-01')),
        ('P03-02 source hierarchy A-D', lambda r: _contains_all(_path(r, 'part_03.source_levels'), ['A','B','C','D'], 'P03-02')),
        ('P03-03 iterative stop conditions', lambda r: len(_path(r, 'part_03.iterative_stop_conditions')) == 3),
        ('P03-04 contradiction detector', lambda r: _path(r, 'part_03.contradiction_detection') is True),
        ('P03-05 citation graph', lambda r: _path(r, 'part_03.citation_graph') is True),
        ('P03-06 knowledge gaps', lambda r: _path(r, 'part_03.knowledge_gap_detection') is True),
        ('P03-07 red team', lambda r: _path(r, 'part_03.red_team') is True),
        ('P03-08 confidence calibration', lambda r: _path(r, 'part_03.confidence_calibration') is True),
        ('P03-09 research gate', lambda r: _path(r, 'part_03.quality_gate') is True),
        ('P04-01 decision definition', lambda r: len(_path(r, 'part_04.decision_definition')) == 8),
        ('P04-02 >=5 realistic', lambda r: sum(o['type']=='realistic' for o in _path(r, 'part_04.options')) >= 5),
        ('P04-03 >=2 unconventional', lambda r: sum(o['type']=='unconventional' for o in _path(r, 'part_04.options')) >= 2),
        ('P04-04 >=1 disruptive', lambda r: sum(o['type']=='disruptive' for o in _path(r, 'part_04.options')) >= 1),
        ('P04-05 score fields', lambda r: _contains_all(_path(r, 'part_04.option_score_fields'), ['strategic_value','financial_value','operational_complexity','implementation_time','capital_requirement','execution_risk','scalability','resilience','expected_roi','expected_npv','confidence'], 'P04-05')),
        ('P04-06 five scenarios', lambda r: _contains_all(_path(r, 'part_04.scenario_set'), ['best_case','expected_case','worst_case','stress_case','black_swan_case'], 'P04-06')),
        ('P04-07 risk categories', lambda r: len(_path(r, 'part_04.risk_categories')) == 10),
        ('P04-08 monte carlo ready', lambda r: _path(r, 'part_04.monte_carlo.status') == 'ready'),
        ('P04-09 impact dimensions', lambda r: len(_path(r, 'part_04.impact_dimensions')) == 10),
        ('P05-01 roles', lambda r: len(_path(r, 'part_05.roles')) >= 13),
        ('P05-02 diagnostic', lambda r: len(_path(r, 'part_05.diagnostic')) >= 14),
        ('P05-03 ratios', lambda r: len(_path(r, 'part_05.ratios')) >= 18),
        ('P05-04 valuations', lambda r: _contains_all(_path(r, 'part_05.valuations'), ['DCF','Comparable Companies','Comparable Transactions','NAV','Replacement Cost','Residual Income','Dividend Discount','Real Options','Commodity Asset Valuation','Mining Asset Valuation'], 'P05-04')),
        ('P05-05 capital budgeting', lambda r: _contains_all(_path(r, 'part_05.capital_budgeting'), ['NPV','IRR','Modified IRR','Payback','Discounted Payback','Profitability Index','Sensitivity Analysis','Scenario Analysis'], 'P05-05')),
        ('P05-06 forecast', lambda r: len(_path(r, 'part_05.forecast')) >= 7),
        ('P05-07 risk', lambda r: len(_path(r, 'part_05.risk')) == 10),
        ('P05-08 stress cases', lambda r: _contains_all(_path(r, 'part_05.stress_cases'), ['Base Case','Best Case','Worst Case','Stress Case','Extreme Case'], 'P05-08')),
        ('P05-09 financial quality controls', lambda r: len(_path(r, 'part_05.quality_controls')) == 7),
        ('P06-01 domains', lambda r: len(_path(r, 'part_06.domains')) >= 18),
        ('P06-02 identification', lambda r: len(_path(r, 'part_06.identification')) == 10),
        ('P06-03 ore quality', lambda r: len(_path(r, 'part_06.ore_quality')) == 9),
        ('P06-04 penalties', lambda r: len(_path(r, 'part_06.penalties')) == 13),
        ('P06-05 metallurgy', lambda r: len(_path(r, 'part_06.metallurgy')) == 8),
        ('P06-06 resource classes', lambda r: len(_path(r, 'part_06.resources')) >= 8),
        ('P06-07 trading', lambda r: len(_path(r, 'part_06.trading')) >= 10),
        ('P06-08 payability', lambda r: len(_path(r, 'part_06.payability')) >= 6),
        ('P06-09 contract review', lambda r: len(_path(r, 'part_06.contract')) >= 9),
        ('P07-01 sector', lambda r: len(_path(r, 'part_07.sector')) >= 9),
        ('P07-02 value chain', lambda r: len(_path(r, 'part_07.value_chain')) >= 9),
        ('P07-03 upstream', lambda r: len(_path(r, 'part_07.upstream')) >= 9),
        ('P07-04 midstream', lambda r: len(_path(r, 'part_07.midstream')) >= 8),
        ('P07-05 downstream', lambda r: len(_path(r, 'part_07.downstream')) >= 7),
        ('P07-06 market drivers', lambda r: len(_path(r, 'part_07.energy_market')) >= 10),
        ('P07-07 commodity prices', lambda r: _contains_all(_path(r, 'part_07.prices'), ['WTI','Brent','Dubai','Henry Hub','TTF','JKM','Coal','Electricity','Carbon','Hydrogen'], 'P07-07')),
        ('P07-08 ESG', lambda r: len(_path(r, 'part_07.esg')) >= 14),
        ('P07-09 sustainability reporting', lambda r: len(_path(r, 'part_07.reporting')) == 10),
        ('P08-01 session memory', lambda r: len(_path(r, 'part_08.session_memory')) == 9),
        ('P08-02 compression', lambda r: len(_path(r, 'part_08.compression')) == 4),
        ('P08-03 hierarchy', lambda r: len(_path(r, 'part_08.hierarchy')) == 5),
        ('P08-04 priority', lambda r: len(_path(r, 'part_08.priority')) == 5),
        ('P08-05 knowledge graph', lambda r: len(_path(r, 'part_08.knowledge_graph')) == 10),
        ('P08-06 decision ledger', lambda r: len(_path(r, 'part_08.decision_ledger')) == 8),
        ('P08-07 anti degradation', lambda r: len(_path(r, 'part_08.anti_degradation')) == 8),
        ('P08-08 self audit', lambda r: len(_path(r, 'part_08.self_audit')) == 7),
        ('P08-09 memory context', lambda r: isinstance(memory_context(), dict)),
        ('P09-01 lifecycle levels', lambda r: _contains_all(_path(r, 'part_09.levels'), ['A','B','C','D','E'], 'P09-01')),
        ('P09-02 temporal', lambda r: len(_path(r, 'part_09.temporal')) == 7),
        ('P09-03 evidence governance', lambda r: len(_path(r, 'part_09.evidence')) == 7),
        ('P09-04 decision gate', lambda r: len(_path(r, 'part_09.decision_gate')) == 7),
        ('P09-05 numerical governance', lambda r: len(_path(r, 'part_09.numerical')) == 9),
        ('P09-06 audit traceability', lambda r: len(_path(r, 'part_09.audit')) == 8),
        ('P09-07 consistency engine', lambda r: len(_path(r, 'part_09.consistency')) == 9),
        ('P09-08 contradiction resolution', lambda r: len(_path(r, 'part_09.contradictions')) == 5),
        ('P09-09 uncertainty and hallucination', lambda r: len(_path(r, 'part_09.uncertainty')) == 6 and len(_path(r, 'part_09.hallucination')) == 7),
        ('P10-01 profiles', lambda r: len(_path(r, 'part_10.profiles')) >= 13),
        ('P10-02 density', lambda r: len(_path(r, 'part_10.density')) == 7),
        ('P10-03 executive structure', lambda r: _contains_all(_path(r, 'part_10.structure'), ['Executive Summary','Key Findings','Evidence','Analysis','Options','Risk Matrix','Recommendation','Implementation','Confidence'], 'P10-03')),
        ('P10-04 action engine', lambda r: _contains_all(_path(r, 'part_10.actions'), ['Immediate Actions','30-Day Plan','90-Day Plan','Long-Term Roadmap','KPIs','Milestones'], 'P10-04')),
        ('P10-05 visual structure', lambda r: len(_path(r, 'part_10.visual')) == 9),
        ('P10-06 deliverable check', lambda r: len(_path(r, 'part_10.quality')) == 7),
        ('P10-07 output profile decision memo', lambda r: _path(r, 'part_01.profile.expected_output') == 'decision memo'),
        ('P10-08 confidence included', lambda r: 'Confidence' in _path(r, 'part_10.structure')),
        ('P10-09 implementation readiness', lambda r: 'Implementation Readiness' in _path(r, 'part_10.quality')),
        ('P11-01 mission detection', lambda r: _nonempty(_path(r, 'part_11.master_runtime.mission_detection'), 'P11-01')),
        ('P11-02 task classification', lambda r: _nonempty(_path(r, 'part_11.master_runtime.task_classification'), 'P11-02')),
        ('P11-03 domain routing', lambda r: _nonempty(_path(r, 'part_11.master_runtime.domain_routing'), 'P11-03')),
        ('P11-04 execution mode', lambda r: _nonempty(_path(r, 'part_11.master_runtime.execution_mode'), 'P11-04')),
        ('P11-05 adaptive depth', lambda r: _nonempty(_path(r, 'part_11.master_runtime.adaptive_depth'), 'P11-05')),
        ('P11-06 pipeline start', lambda r: _path(r, 'part_11.master_runtime.pipeline')[0] == 'Mission Detection'),
        ('P11-07 pipeline end', lambda r: _path(r, 'part_11.master_runtime.pipeline')[-1] == 'Output Compiler'),
        ('P11-08 conflict resolution', lambda r: _contains_all(_path(r, 'part_11.master_runtime.conflict_resolution'), ['Evidence','Logic','Freshness','Domain Authority','Consistency'], 'P11-08')),
        ('P11-09 fail safe', lambda r: len(_path(r, 'part_11.master_runtime.fail_safe')) == 4),
    ]


def test_omega_spec_has_99_atomic_controls():
    assert len(_manifest()) == 99


def test_omega_spec_audit_all_controls_pass():
    report = build_strict_runtime('Research an oil & gas investment decision under regulatory risk with verified evidence and a board memo.', evidence_count=3)
    failures: list[str] = []
    for label, control in _manifest():
        try:
            if not bool(control(report)):
                failures.append(label)
        except Exception as exc:
            failures.append(f'{label}::{exc}')
    assert not failures, 'STRICT_SPEC_AUDIT_FAILURES:\n' + '\n'.join(failures)


def test_strict_audit_blocks_release_without_required_research_evidence():
    blocked = build_strict_runtime('Research current oil & gas regulatory risk and recommend a decision.', evidence_count=0)
    assert blocked['gate']['evidence_ready'] is False
    assert blocked['gate']['release_ready'] is False


def test_strict_audit_finance_calculations_are_operational():
    cashflows = [-100.0, 60.0, 60.0]
    assert npv(0.10, cashflows) > 0
    assert irr(cashflows) is not None
    assert modified_irr(cashflows, 0.10, 0.10) is not None
    assert payback_period(cashflows) is not None
    ratios = ratio_engine({'revenue':200,'gross_profit':80,'ebitda':50,'operating_income':40,'net_income':30,'assets':300,'equity':150,'debt':100,'cash':40,'current_assets':120,'current_liabilities':60,'inventory':30,'interest_expense':10,'cogs':120,'receivables':20,'payables':15})
    assert ratios['current_ratio'] == 2
    assert ratios['debt_to_equity'] == 100/150
    assert valuation_dcf([20,25,30], 0.10, 0.02) > 0
    assert quality_score({k:100 for k in ['accuracy','evidence','depth','reasoning','consistency','completeness','executive_value','actionability','traceability']}) == 100


def test_strict_audit_mining_controls_are_operational():
    assert unit_consistency(['%','ppm','g/t','DMT','oz'])
    penalties = mining_penalties({'As':0.5,'Hg':0,'S':2.0})
    assert set(penalties['detected']) == {'As','Hg','S'}
    domain = mining_domain({'commodity':'antimony','country':'X','head_grade':12.0,'recovery_pct':85.0})
    assert domain['commodity'] == 'antimony'
    terms = trading_terms({'incoterm':'CIF','payability_pct':90})
    assert terms['incoterm'] == 'CIF'


def test_strict_audit_energy_and_esg_controls_are_operational():
    sector = energy_domain({'industry':'Oil & Gas','subsector':'LNG','value_chain':'Midstream'})
    assert sector['industry'] == 'Oil & Gas'
    market = energy_market({'wti':70,'brent':75,'ttf':35,'jkm':12})
    assert market['commodity_prices']['WTI'] == 70
    esg = esg_assessment({'methane':'high','water_risk':'medium'})
    assert esg['methane'] == 'high'
    reporting = sustainability_reporting({'IFRS S1':True,'ISSB':True})
    assert reporting['IFRS S1'] is True


def test_strict_audit_memory_and_decision_ledger_are_operational():
    mem = memory_context()
    assert 'session' in mem and 'hierarchy' in mem and 'priority' in mem
    entry = decision_ledger_entry('Proceed','Evidence supports',97)
    assert entry['decision_id'].startswith('DEC-')
    assert entry['confidence'] == 97


def test_strict_audit_rejects_placeholder_markers_in_release_artifact():
    report = build_strict_runtime('Build an executive analysis from verified evidence with a decision memo.', evidence_count=3)
    serialized = repr(report)
    forbidden = [m for m in PLACEHOLDER_MARKERS if m in serialized and m not in ('assessment_placeholder_allowed',)]
    assert forbidden == [], f'placeholder_markers_present:{forbidden}'
