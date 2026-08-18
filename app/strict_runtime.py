from __future__ import annotations

from typing import Any


def _evidence_confidence(e: Any) -> float:
    values = [
        getattr(e, "authority", 0.0),
        getattr(e, "accuracy", 0.0),
        getattr(e, "freshness", 0.0),
        getattr(e, "transparency", 0.0),
        getattr(e, "evidence", 0.0),
        100.0 - getattr(e, "bias_risk", 100.0),
        getattr(e, "replicability", 0.0),
    ]
    return sum(values) / len(values)


def patch_omega_compliance(mod: Any) -> Any:
    original_classify = mod.classify_request

    def classify_request(text: str) -> dict[str, Any]:
        p = original_classify(text)
        t = text.lower()
        matched = [d for d in mod.DOMAINS if d in t]
        p["primary_domain"] = matched[0] if matched else "general"
        p["secondary_domains"] = matched[1:]
        # Explicit research is a research mission even when the request also asks for a decision/recommendation.
        if any(x in t for x in ("research", "investigate", "research an", "research the")):
            p["mission"] = "research"
        elif any(x in t for x in ("should we", "recommend", "decide", "decision", "choose")):
            p["mission"] = "decision"
        else:
            p["mission"] = "analysis"
        return p

    mod.classify_request = classify_request

    if not hasattr(mod.Evidence, "confidence"):
        mod.Evidence.confidence = property(_evidence_confidence)

    original_master = mod.master_runtime

    def master_runtime(text: str) -> dict[str, Any]:
        result = original_master(text)
        result["profile"] = classify_request(text)
        result["mission"] = result["profile"]["mission"]
        if result["mission"] == "research":
            result["execution_mode"] = "maximum precision" if result["profile"]["decision_risk"] == "high" else result.get("execution_mode", "deep")
        return result

    mod.master_runtime = master_runtime
    return mod
