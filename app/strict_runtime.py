from __future__ import annotations

from typing import Any


def _evidence_confidence(e: Any) -> float:
    values = [
        getattr(e, "authority", 0.0), getattr(e, "accuracy", 0.0),
        getattr(e, "freshness", 0.0), getattr(e, "transparency", 0.0),
        getattr(e, "evidence", 0.0), 100.0 - getattr(e, "bias_risk", 100.0),
        getattr(e, "replicability", 0.0),
    ]
    return sum(values) / len(values)


def patch_omega_compliance(mod: Any) -> Any:
    original_classify = mod.classify_request

    def classify_request(text: str) -> dict[str, Any]:
        p = original_classify(text); t = text.lower()
        matched = [d for d in mod.DOMAINS if d in t]
        if "oil & gas" in t or ("oil" in t and "gas" in t): primary = "oil & gas"
        elif any(term in t for term in ("finance", "investment", "accounting", "npv", "irr", "valuation", "financial")): primary = "finance"
        elif matched: primary = matched[0]
        else: primary = "general"
        p["primary_domain"] = primary
        p["secondary_domains"] = [d for d in matched if d != primary]
        if any(x in t for x in ("research", "investigate", "research an", "research the")): p["mission"] = "research"
        elif any(x in t for x in ("should we", "recommend", "decide", "decision", "choose")): p["mission"] = "decision"
        else: p["mission"] = "analysis"
        if any(x in t for x in ("decision memo", "board memo", "investment memo")): p["expected_output"] = "decision memo"
        elif "memo" in t and p["mission"] == "decision": p["expected_output"] = "decision memo"
        return p

    mod.classify_request = classify_request
    if not hasattr(mod.Evidence, "confidence"): mod.Evidence.confidence = property(_evidence_confidence)

    original_master = mod.master_runtime
    def master_runtime(text: str) -> dict[str, Any]:
        result = original_master(text); result["profile"] = classify_request(text); result["mission"] = result["profile"]["mission"]
        if result["mission"] == "research": result["execution_mode"] = "maximum precision" if result["profile"]["decision_risk"] == "high" else result.get("execution_mode", "deep")
        return result
    mod.master_runtime = master_runtime

    try:
        from . import omega_strict
        original_energy_runtime = omega_strict.energy_runtime
        original_output_runtime = omega_strict.output_runtime
        def strict_energy_runtime() -> dict[str, Any]:
            result = dict(original_energy_runtime())
            result["sector"] = list(result.get("sector", [])); result["energy_market"] = list(result.get("market", [])); result["esg"] = list(result.get("esg", []))
            return result
        def strict_output_runtime() -> dict[str, Any]:
            result = dict(original_output_runtime())
            result["writing_quality"] = ["C-Suite", "Board Level", "Investment Committee", "Government", "Institutional Investors", "Technical Experts", "precisely", "professionally", "logically", "densely", "clearly", "fluff", "redundancy", "marketing language", "unnecessary repetition", "vague wording", "empty adjectives", "unsupported certainty"]
            result["executive_language"] = ["precisely", "professionally", "logically", "densely", "clearly", "avoid vague wording", "avoid empty adjectives", "avoid unsupported certainty"]
            result["adaptive_formats"] = ["Email", "Proposal", "Tender", "Contract", "Report", "Presentation", "Memo", "LinkedIn", "CV"]
            return result
        omega_strict.energy_runtime = strict_energy_runtime; omega_strict.output_runtime = strict_output_runtime
    except Exception:
        pass

    original_energy_market = mod.energy_market
    def energy_market(data: dict[str, Any]) -> dict[str, Any]:
        result = original_energy_market(data)
        aliases = {"WTI":"wti", "Brent":"brent", "Dubai":"dubai", "Henry Hub":"henry_hub", "TTF":"ttf", "JKM":"jkm", "Coal":"coal", "Electricity":"electricity", "Carbon":"carbon", "Hydrogen":"hydrogen"}
        result["commodity_prices"] = {**{key:data.get(key) for key in aliases.values()}, **{label:data.get(key) for label,key in aliases.items()}}
        return result
    mod.energy_market = energy_market
    return mod
