from app.omega_strict import build_strict_runtime, strict_release_gate, QUALITY_TARGET, PLACEHOLDER_MARKERS


def test_all_eleven_parts_are_present_and_structured():
    r = build_strict_runtime("Research an oil & gas investment decision under regulatory risk.", evidence_count=2)
    for i in range(1, 12):
        assert f"part_{i:02d}" in r
    assert r["spec_version"] == "1.0"
    assert r["part_02"]["root_cause"]["five_whys"] and len(r["part_02"]["root_cause"]["five_whys"]) == 5
    assert len(r["part_02"]["hypotheses"]) >= 3
    assert len(r["part_03"]["source_levels"]) == 4
    assert r["part_04"]["options"] and len(r["part_04"]["options"]) >= 8
    assert sum(o["type"] == "realistic" for o in r["part_04"]["options"]) >= 5
    assert sum(o["type"] == "unconventional" for o in r["part_04"]["options"]) >= 2
    assert sum(o["type"] == "disruptive" for o in r["part_04"]["options"]) >= 1


def test_domain_extensions_cover_required_finance_mining_energy_controls():
    r = build_strict_runtime("Analyze a mining and LNG portfolio with ESG and financial risk.", evidence_count=2)
    finance = r["part_05"]
    assert "NPV" in finance["capital_budgeting"]
    assert "IRR" in finance["capital_budgeting"]
    assert "DCF" in finance["valuations"]
    assert "Cash Conversion Cycle" in finance["ratios"]
    mining = r["part_06"]
    for u in ["%", "ppm", "g/t", "kg/t", "MT", "DMT", "WMT", "lb", "ton", "oz"]:
        assert u in mining["units"]
    for e in ["As", "Hg", "Pb", "Cd", "Bi", "F", "Cl", "Se", "Te", "Cu", "Zn", "Fe", "S"]:
        assert e in mining["penalties"]
    energy = r["part_07"]
    for p in ["WTI", "Brent", "Dubai", "Henry Hub", "TTF", "JKM"]:
        assert p in energy["prices"]
    for f in ["IFRS S1", "IFRS S2", "GRI", "SASB", "TCFD", "ISSB", "CSRD", "GHG Protocol", "CDP", "UN SDGs"]:
        assert f in energy["reporting"]


def test_memory_governance_output_and_master_pipeline_are_complete():
    r = build_strict_runtime("Build a decision-ready executive analysis.", evidence_count=1)
    memory = r["part_08"]
    assert "Decision ID" in memory["decision_ledger"]
    assert "Quality Drift" in memory["anti_degradation"]
    gov = r["part_09"]
    assert len(gov["quality_metrics"]) == 9
    assert "Finding ID" in gov["audit"]
    out = r["part_10"]
    assert "Recommendation" in out["structure"]
    assert "90-Day Plan" in out["actions"]
    pipeline = r["part_11"]["master_runtime"]["pipeline"]
    assert pipeline[0] == "Mission Detection"
    assert pipeline[-1] == "Output Compiler"
    assert len(pipeline) == 11


def test_strict_release_blocks_when_research_has_no_evidence():
    r = build_strict_runtime("Research the current regulatory risk and recommend a decision.", evidence_count=0)
    assert r["gate"]["release_ready"] is False
    assert r["gate"]["evidence_ready"] is False


def test_strict_release_can_pass_structural_gate_with_evidence():
    r = build_strict_runtime("Build an executive analysis from verified evidence.", evidence_count=3)
    assert r["gate"]["quality"] >= QUALITY_TARGET
    assert r["gate"]["release_ready"] is True
    assert not any(m in repr(r) for m in PLACEHOLDER_MARKERS)
