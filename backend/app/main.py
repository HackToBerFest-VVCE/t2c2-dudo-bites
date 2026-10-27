from __future__ import annotations

from typing import Any, Dict, List


def explain_risk_score(
    bot_predictions: List[Dict[str, Any]] | None,
    claim_results: List[Dict[str, Any]] | None,
    coordination_results: List[Dict[str, Any]] | None,
) -> Dict[str, Any]:
    bot_predictions = bot_predictions or []
    claim_results = claim_results or []
    coordination_results = coordination_results or []

    bot_scores = [item.get("bot_probability", 0.0) for item in bot_predictions]
    claim_scores = [item.get("risk_score", 0.0) for item in claim_results]
    coordination_scores = [
        min(100.0, (len(item.get("accounts", [])) * 25.0) + 25.0)
        for item in coordination_results
    ]

    bot_component = sum(bot_scores) / max(len(bot_scores), 1)
    claim_component = sum(claim_scores) / max(len(claim_scores), 1) * 100
    coordination_component = sum(coordination_scores) / max(len(coordination_scores), 1)

    weighted_total = (
        bot_component * 0.45
        + claim_component * 0.35
        + coordination_component * 0.20
    )
    risk_score = min(100.0, round(weighted_total, 2))

    explanation = []
    if bot_predictions:
        explanation.append(f"Bot behavior signal contributes {round(bot_component, 2)}% of the score.")
    else:
        explanation.append("Bot behavior evidence is unavailable for this dataset.")

    if claim_results:
        explanation.append(f"Claim risk contributes {round(claim_component, 2)}% of the score.")
    else:
        explanation.append("Claim-analysis evidence is unavailable; no claim risk was calculated.")

    if coordination_results:
        explanation.append(f"Coordination network contributes {round(coordination_component, 2)}% of the score.")
    else:
        explanation.append("No coordination evidence was detected in the current sample.")

    return {
        "risk_score": risk_score,
        "risk_level": "low" if risk_score < 35 else "medium" if risk_score < 70 else "high",
        "bot_signal_score": round(bot_component, 2),
        "claim_signal_score": round(claim_component, 2),
        "coordination_signal_score": round(coordination_component, 2),
        "evidence_count": len(bot_predictions) + len(claim_results) + len(coordination_results),
        "explanation": explanation,
    }
