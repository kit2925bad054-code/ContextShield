def combine(rule_result, ai_result=None):
    if not ai_result:
        return rule_result
    # Keep deterministic rule result available for auditability.
    return {
        **ai_result,
        "hybrid_rule_score": rule_result.get("risk_score"),
        "engine": "hybrid"
    }
