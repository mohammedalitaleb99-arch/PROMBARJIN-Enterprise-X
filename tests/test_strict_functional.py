from app.omega_strict import build_strict_runtime, classification, npv, irr, modified_irr, payback, discounted_payback, profitability_index


def test_research_mission_requires_evidence_for_release():
    blocked = build_strict_runtime("Research current oil & gas regulatory risk and recommend a decision.", evidence_count=0)
    assert blocked["profile"]["mission"] == "research"
    assert blocked["gate"]["release_ready"] is False
    passed = build_strict_runtime("Research current oil & gas regulatory risk and recommend a decision from verified evidence.", evidence_count=3)
    assert passed["gate"]["evidence_ready"] is True


def test_high_risk_research_uses_maximum_precision():
    p = classification("Research an oil & gas investment under regulatory and compliance risk.")
    assert p["decision_risk"] == "high"
    assert p["required_depth"] == "maximum precision"
    assert p["evidence_requirement"] == "high"


def test_financial_capital_budgeting_functions_are_numeric_and_consistent():
    flows = [-100, 40, 40, 40, 40]
    assert npv(0.10, flows) > 0
    r = irr(flows)
    assert r is not None and -1 < r < 10
    m = modified_irr(flows, 0.10, 0.10)
    assert m is not None
    p = payback(flows)
    dp = discounted_payback(0.10, flows)
    pi = profitability_index(0.10, flows)
    assert p is not None and dp is not None and pi is not None


def test_mining_and_energy_domain_selection_is_automatic():
    mining = build_strict_runtime("Analyze an antimony concentrate with JORC resources, assay penalties, payability and CIF logistics.", evidence_count=3)
    assert mining["profile"]["primary_domain"] in {"mining", "critical minerals", "antimony", "commodity trading", "finance"}
    assert "As" in mining["part_06"]["penalties"]
    assert "DMT" in mining["part_06"]["units"]

    energy = build_strict_runtime("Analyze an LNG portfolio with Brent exposure, TTF, JKM, methane, IFRS S2 and climate transition risk.", evidence_count=3)
    assert "Brent" in energy["part_07"]["prices"]
    assert "TTF" in energy["part_07"]["prices"]
    assert "JKM" in energy["part_07"]["prices"]
    assert "IFRS S2" in energy["part_07"]["reporting"]


def test_decision_runtime_contains_required_option_classes_and_scenarios():
    r = build_strict_runtime("Recommend the best strategic investment option under high uncertainty.", evidence_count=3)
    opts = r["part_04"]["options"]
    assert sum(o["type"] == "realistic" for o in opts) >= 5
    assert sum(o["type"] == "unconventional" for o in opts) >= 2
    assert sum(o["type"] == "disruptive" for o in opts) >= 1
    assert set(r["part_04"]["scenario_set"]) == {"best_case", "expected_case", "worst_case", "stress_case", "black_swan_case"}


def test_memory_governance_and_output_are_present_in_live_runtime():
    r = build_strict_runtime("Prepare an executive decision memo with next actions and confidence.", evidence_count=3)
    assert r["part_08"]["decision_ledger"]
    assert r["part_09"]["audit"]
    assert r["part_09"]["quality_metrics"]
    assert r["part_10"]["structure"]
    assert r["part_10"]["actions"]
    assert r["part_11"]["master_runtime"]["pipeline"][-1] == "Output Compiler"


def test_strict_runtime_never_releases_with_unresolved_placeholder_markers():
    r = build_strict_runtime("Build a verified executive analysis.", evidence_count=3)
    assert r["gate"]["release_ready"] is True
    rendered = repr(r).upper()
    for marker in ["TODO", "FIXME", "TBD", "PLACEHOLDER", "IMPLEMENT LATER"]:
        assert marker not in rendered
