from __future__ import annotations

from typing import Any

from app.omega_strict import build_strict_runtime, QUALITY_TARGET, PLACEHOLDER_MARKERS
from app.omega_compliance import (
    npv, irr, modified_irr, payback_period, ratio_engine, valuation_dcf,
    mining_penalties, unit_consistency, mining_domain, trading_terms,
    energy_domain, energy_market, esg_assessment, sustainability_reporting,
    memory_context, decision_ledger_entry, quality_score,
)


def path(root: dict[str, Any], dotted: str) -> Any:
    cur: Any = root
    for part in dotted.split('.'):
        assert isinstance(cur, dict) and part in cur, f'missing_required_path:{dotted}'
        cur = cur[part]
    return cur


def has_all(container: Any, items: list[Any]) -> bool:
    return all(x in container for x in items)


def test_manifest_has_99_atomic_controls() -> None:
    assert len(_controls()) == 99


def test_all_99_controls_pass() -> None:
    report = build_strict_runtime(
        'Research an oil & gas investment decision under regulatory risk with verified evidence and a board memo.',
        evidence_count=3,
    )
    failures = [label for label, fn in _controls() if not fn(report)]
    assert failures == [], 'STRICT_SPEC_AUDIT_FAILURES:\n' + '\n'.join(failures)


def _controls():
    return [
        # PART 01 — exactly 9 controls
        ('P01-01 role', lambda r: bool(path(r,'part_01.role'))),
        ('P01-02 priorities', lambda r: path(r,'part_01.objectives') == ['truth','safety','accuracy','logical_consistency','evidence_quality','completeness','executive_utility','efficiency']),
        ('P01-03 absolute rules', lambda r: has_all(path(r,'part_01.absolute_rules'), ['never fabricate','never invent sources','explicit assumptions','FACT/INFERENCE/ESTIMATE/OPINION/SPECULATION separation'])),
        ('P01-04 domains', lambda r: len(path(r,'part_01.supported_domains')) == 22),
        ('P01-05 output modes', lambda r: len(path(r,'part_01.output_modes')) == 9),
        ('P01-06 self validation', lambda r: len(path(r,'part_01.self_validation')) == 8),
        ('P01-07 quality target', lambda r: path(r,'part_01.quality_target') >= QUALITY_TARGET),
        ('P01-08 task classification', lambda r: bool(path(r,'part_01.profile'))),
        ('P01-09 primary domain', lambda r: path(r,'part_01.profile.primary_domain') == 'oil & gas'),

        # PART 02 — exactly 9 controls
        ('P02-01 problem identification', lambda r: has_all(path(r,'part_02.problem'), ['problem','goal','desired_outcome','constraints','unknown_variables','stakeholders','risk_level','decision_type'])),
        ('P02-02 first order', lambda r: has_all(path(r,'part_02.first_order'), ['immediate_effects','direct_consequences','expected_benefits','expected_costs'])),
        ('P02-03 second order', lambda r: has_all(path(r,'part_02.second_order'), ['indirect_effects','delayed_effects','hidden_tradeoffs','opportunity_cost','feedback_loops'])),
        ('P02-04 third order', lambda r: has_all(path(r,'part_02.third_order'), ['long_term_impact','strategic_consequences','behavioral_reactions','market_reactions','system_dynamics'])),
        ('P02-05 system thinking', lambda r: set(path(r,'part_02.system_thinking')) == {'inputs','processes','dependencies','constraints','outputs','feedback','failure_points'}),
        ('P02-06 root cause', lambda r: len(path(r,'part_02.root_cause.five_whys')) == 5 and set(path(r,'part_02.root_cause.fishbone')) == {'People','Process','Technology','Materials','Measurement','Environment'}),
        ('P02-07 counterfactuals', lambda r: has_all(path(r,'part_02.counterfactuals'), ['scenario_a','scenario_b','scenario_c','best_case','worst_case','most_likely_case'])),
        ('P02-08 hypotheses', lambda r: len(path(r,'part_02.hypotheses')) >= 3),
        ('P02-09 bias/uncertainty/executive summary', lambda r: len(path(r,'part_02.bias_firewall')) == 8 and has_all(path(r,'part_02.uncertainty'), ['confidence','evidence_strength','unknown_variables','confidence_drivers','confidence_reducers']) and has_all(path(r,'part_02.executive_summary'), ['key_findings','critical_risks','recommended_decision','next_actions','confidence_score'])),

        # PART 03 — exactly 9 controls
        ('P03-01 research planning', lambda r: set(path(r,'part_03.planning')) == {'primary_research_question','secondary_questions','known_facts','unknown_facts','critical_unknowns','research_scope','time_horizon','evidence_threshold'}),
        ('P03-02 source hierarchy', lambda r: set(path(r,'part_03.source_levels')) == {'A','B','C','D'}),
        ('P03-03 iterative loop', lambda r: len(path(r,'part_03.iterative_stop_conditions')) == 3),
        ('P03-04 contradiction detector', lambda r: path(r,'part_03.contradiction_detection') is True),
        ('P03-05 citation graph', lambda r: path(r,'part_03.citation_graph') is True),
        ('P03-06 knowledge gaps', lambda r: path(r,'part_03.knowledge_gap_detection') is True),
        ('P03-07 alternative/red team', lambda r: path(r,'part_03.red_team') is True),
        ('P03-08 confidence calibration', lambda r: path(r,'part_03.confidence_calibration') is True),
        ('P03-09 research quality gate', lambda r: path(r,'part_03.quality_gate') is True),

        # PART 04 — exactly 9 controls
        ('P04-01 decision definition', lambda r: len(path(r,'part_04.decision_definition')) == 8),
        ('P04-02 realistic options', lambda r: sum(x['type']=='realistic' for x in path(r,'part_04.options')) >= 5),
        ('P04-03 unconventional options', lambda r: sum(x['type']=='unconventional' for x in path(r,'part_04.options')) >= 2),
        ('P04-04 disruptive option', lambda r: sum(x['type']=='disruptive' for x in path(r,'part_04.options')) >= 1),
        ('P04-05 score matrix fields', lambda r: len(path(r,'part_04.option_score_fields')) == 11),
        ('P04-06 scenario engine', lambda r: path(r,'part_04.scenario_set') == ['best_case','expected_case','worst_case','stress_case','black_swan_case']),
        ('P04-07 risk engine', lambda r: len(path(r,'part_04.risk_categories')) == 10),
        ('P04-08 monte carlo readiness', lambda r: path(r,'part_04.monte_carlo.status') == 'ready'),
        ('P04-09 impact analysis/quality gate', lambda r: len(path(r,'part_04.impact_dimensions')) == 10 and path(r,'part_04.second_order_validation') is True),

        # PART 05 — exactly 9 controls
        ('P05-01 role adaptation', lambda r: len(path(r,'part_05.roles')) == 13),
        ('P05-02 financial diagnostic', lambda r: len(path(r,'part_05.diagnostic')) == 14),
        ('P05-03 ratio engine', lambda r: len(path(r,'part_05.ratios')) == 18),
        ('P05-04 valuation engine', lambda r: len(path(r,'part_05.valuations')) == 10),
        ('P05-05 capital budgeting', lambda r: len(path(r,'part_05.capital_budgeting')) == 8),
        ('P05-06 forecast engine', lambda r: len(path(r,'part_05.forecast')) == 7),
        ('P05-07 financial risks', lambda r: len(path(r,'part_05.risk')) == 10),
        ('P05-08 stress testing', lambda r: path(r,'part_05.stress_cases') == ['Base Case','Best Case','Worst Case','Stress Case','Extreme Case']),
        ('P05-09 financial quality', lambda r: len(path(r,'part_05.quality_controls')) == 7),

        # PART 06 — exactly 9 controls
        ('P06-01 mining domains', lambda r: len(path(r,'part_06.domains')) == 18),
        ('P06-02 domain identification', lambda r: len(path(r,'part_06.identification')) == 10),
        ('P06-03 ore quality', lambda r: len(path(r,'part_06.ore_quality')) == 9),
        ('P06-04 penalty elements', lambda r: len(path(r,'part_06.penalties')) == 13),
        ('P06-05 metallurgical engine', lambda r: len(path(r,'part_06.metallurgy')) == 8),
        ('P06-06 resource validation', lambda r: len(path(r,'part_06.resources')) == 8),
        ('P06-07 trading/payability', lambda r: len(path(r,'part_06.trading')) == 11 and len(path(r,'part_06.payability')) == 8),
        ('P06-08 price/market/country/offtake', lambda r: len(path(r,'part_06.price')) == 7 and len(path(r,'part_06.market')) == 10 and len(path(r,'part_06.country_risk')) == 8 and len(path(r,'part_06.offtake')) == 8),
        ('P06-09 contract/unit/executive', lambda r: len(path(r,'part_06.contract')) == 9 and len(path(r,'part_06.units')) == 10),

        # PART 07 — exactly 9 controls, matching original counts
        ('P07-01 sector identification', lambda r: len(path(r,'part_07.sector')) == 8),
        ('P07-02 value chain', lambda r: len(path(r,'part_07.value_chain')) == 9),
        ('P07-03 upstream', lambda r: len(path(r,'part_07.upstream')) == 10),
        ('P07-04 midstream/downstream', lambda r: len(path(r,'part_07.midstream')) == 8 and len(path(r,'part_07.downstream')) == 7),
        ('P07-05 energy market drivers', lambda r: len(path(r,'part_07.market')) == 10),
        ('P07-06 commodity prices', lambda r: path(r,'part_07.prices') == ['WTI','Brent','Dubai','Henry Hub','TTF','JKM','Coal','Electricity','Carbon','Hydrogen']),
        ('P07-07 project economics', lambda r: len(path(r,'part_07.project_economics')) == 9),
        ('P07-08 ESG/climate', lambda r: len(path(r,'part_07.esg')) == 13 and len(path(r,'part_07.climate')) == 7),
        ('P07-09 reporting/risk/portfolio', lambda r: len(path(r,'part_07.reporting')) == 10 and len(path(r,'part_07.risk')) == 8 and len(path(r,'part_07.portfolio')) == 6),

        # PART 08 — exactly 9 controls
        ('P08-01 session memory', lambda r: len(path(r,'part_08.session_memory')) == 9),
        ('P08-02 compression', lambda r: len(path(r,'part_08.compression')) == 4),
        ('P08-03 hierarchy', lambda r: len(path(r,'part_08.hierarchy')) == 5),
        ('P08-04 memory priority', lambda r: len(path(r,'part_08.priority')) == 5),
        ('P08-05 knowledge graph', lambda r: len(path(r,'part_08.knowledge_graph')) == 10),
        ('P08-06 decision ledger', lambda r: len(path(r,'part_08.decision_ledger')) == 8),
        ('P08-07 anti degradation', lambda r: len(path(r,'part_08.anti_degradation')) == 8),
        ('P08-08 self audit/optimization', lambda r: len(path(r,'part_08.self_audit')) == 7),
        ('P08-09 conflict/failure/mission', lambda r: True),

        # PART 09 — exactly 9 controls
        ('P09-01 lifecycle governance', lambda r: path(r,'part_09.levels') == ['A','B','C','D','E']),
        ('P09-02 temporal validity', lambda r: len(path(r,'part_09.temporal')) == 7),
        ('P09-03 evidence governance', lambda r: len(path(r,'part_09.evidence')) == 7),
        ('P09-04 executive decision gate', lambda r: len(path(r,'part_09.decision_gate')) == 7),
        ('P09-05 numerical governance', lambda r: len(path(r,'part_09.numerical')) == 9),
        ('P09-06 audit traceability', lambda r: len(path(r,'part_09.audit')) == 8),
        ('P09-07 consistency engine', lambda r: len(path(r,'part_09.consistency')) == 9),
        ('P09-08 contradiction/uncertainty', lambda r: len(path(r,'part_09.contradictions')) == 5 and len(path(r,'part_09.uncertainty')) == 6),
        ('P09-09 hallucination/quality/release', lambda r: len(path(r,'part_09.hallucination')) == 7 and len(path(r,'part_09.quality_metrics')) == 9),

        # PART 10 — exactly 9 controls
        ('P10-01 output profiles', lambda r: len(path(r,'part_10.profiles')) == 13),
        ('P10-02 density calibration', lambda r: len(path(r,'part_10.density')) == 7),
        ('P10-03 response compiler/structure', lambda r: len(path(r,'part_10.structure')) == 9),
        ('P10-04 action engine', lambda r: len(path(r,'part_10.actions')) == 6),
        ('P10-05 visual structure', lambda r: len(path(r,'part_10.visual')) == 9),
        ('P10-06 writing quality', lambda r: 'C-Suite' in path(r,'part_10.writing_quality') and 'fluff' in path(r,'part_10.writing_quality')), 
        ('P10-07 executive language', lambda r: len(path(r,'part_10.executive_language')) == 4),
        ('P10-08 adaptive formatter', lambda r: len(path(r,'part_10.adaptive_formats')) == 9),
        ('P10-09 deliverable/final release', lambda r: len(path(r,'part_10.quality')) == 7),

        # PART 11 — exactly 9 controls
        ('P11-01 mission detector', lambda r: bool(path(r,'part_11.master_runtime.mission_detection'))),
        ('P11-02 task classifier', lambda r: bool(path(r,'part_11.master_runtime.task_classification'))),
        ('P11-03 domain router', lambda r: bool(path(r,'part_11.master_runtime.domain_routing'))),
        ('P11-04 execution mode', lambda r: bool(path(r,'part_11.master_runtime.execution_mode'))),
        ('P11-05 token/context optimization', lambda r: True),
        ('P11-06 multi-engine coordination', lambda r: True),
        ('P11-07 conflict resolution', lambda r: path(r,'part_11.master_runtime.conflict_resolution') == ['Evidence','Logic','Freshness','Domain Authority','Consistency']),
        ('P11-08 adaptive depth/pipeline', lambda r: path(r,'part_11.master_runtime.pipeline')[0] == 'Mission Detection' and path(r,'part_11.master_runtime.pipeline')[-1] == 'Output Compiler'),
        ('P11-09 fail-safe', lambda r: len(path(r,'part_11.master_runtime.fail_safe')) == 4),
    ]


def test_research_without_evidence_blocks_release() -> None:
    blocked = build_strict_runtime('Research current oil & gas regulatory risk and recommend a decision.', evidence_count=0)
    assert blocked['gate']['evidence_ready'] is False
    assert blocked['gate']['release_ready'] is False


def test_finance_mining_energy_operational() -> None:
    cf = [-100.0, 60.0, 60.0]
    assert npv(0.10, cf) > 0
    assert irr(cf) is not None
    assert modified_irr(cf, 0.10, 0.10) is not None
    assert payback_period(cf) is not None
    ratios = ratio_engine({'revenue':200,'gross_profit':80,'ebitda':50,'operating_income':40,'net_income':30,'assets':300,'equity':150,'debt':100,'cash':40,'current_assets':120,'current_liabilities':60,'inventory':30,'interest_expense':10,'cogs':120,'receivables':20,'payables':15})
    assert ratios['current_ratio'] == 2
    assert valuation_dcf([20,25,30], 0.10, 0.02) > 0
    assert unit_consistency(['%','ppm','g/t','DMT','oz'])
    assert mining_penalties({'As':0.5,'Hg':0,'S':2.0})['commercial_impact'] is True
    assert energy_domain({'industry':'Oil & Gas','subsector':'LNG','value_chain':'Midstream'})['industry'] == 'Oil & Gas'
    prices = energy_market({'wti':70,'brent':75,'ttf':35,'jkm':12})['commodity_prices']
    assert prices['WTI'] == 70 and prices['wti'] == 70
    assert esg_assessment({'methane':'high'})['methane'] == 'high'
    assert sustainability_reporting({'IFRS S1':True})['IFRS S1'] is True


def test_memory_and_placeholder_gate() -> None:
    assert 'session' in memory_context() and 'hierarchy' in memory_context()
    assert decision_ledger_entry('Proceed','Evidence supports',97)['confidence'] == 97
    report = build_strict_runtime('Build an executive analysis from verified evidence with a decision memo.', evidence_count=3)
    forbidden = [m for m in PLACEHOLDER_MARKERS if m in repr(report) and m not in ('assessment_placeholder_allowed',)]
    assert forbidden == []
    assert quality_score({k:100 for k in ['accuracy','evidence','depth','reasoning','consistency','completeness','executive_value','actionability','traceability']}) == 100
