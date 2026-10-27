from backend.app.services.risk_scoring_service import explain_risk_score


def test_risk_score_is_calculated_and_bounded():
    result = explain_risk_score(
        bot_predictions=[{"bot_probability": 80.0}],
        claim_results=[{"risk_score": 0.7}],
        coordination_results=[{"accounts": ["u1", "u2", "u3"]}],
    )

    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in {"low", "medium", "high"}
    assert result["evidence_count"] >= 3
    assert isinstance(result["explanation"], list)


def test_risk_score_handles_missing_evidence_gracefully():
    result = explain_risk_score([], [], [])

    assert result["risk_score"] == 0.0
    assert "unavailable" in " ".join(result["explanation"]).lower()
