from __future__ import annotations

from typing import Any


def analyze_account(account: dict[str, Any]) -> dict[str, Any]:
    """Transparent rule-based baseline used for the MVP.

    This does not prove an account is a bot; it produces a review signal only.
    """
    followers = float(account.get("followers", 0) or 0)
    following = float(account.get("following", 0) or 0)
    account_age_days = float(account.get("account_age_days", 0) or 0)
    post_count_7d = float(account.get("post_count_7d", 0) or 0)
    repetition_score = float(account.get("repetition_score", 0.0) or 0.0)
    burstiness = float(account.get("burstiness", 0.0) or 0.0)

    ratio = followers / max(following, 1)
    risk_score = 0.0

    if following > 0 and ratio < 0.25:
        risk_score += 20
    if post_count_7d >= 25:
        risk_score += 20
    if repetition_score >= 0.7:
        risk_score += 20
    if burstiness >= 0.7:
        risk_score += 20
    if account_age_days <= 14 and following > 1000 and followers < 500:
        risk_score += 15
    if post_count_7d >= 40 and following >= 1000:
        risk_score += 15

    score = max(0.0, min(100.0, risk_score))
    if score >= 70:
        label = "Likely suspicious"
    elif score >= 45:
        label = "Needs review"
    else:
        label = "Low suspicion"

    return {
        "account_id": account.get("account_id", "unknown"),
        "bot_probability": round(score, 2),
        "bot_label": label,
        "model_type": "rule-based baseline",
        "reason": (
            "This is a transparent heuristic risk signal, not proof of automated bot activity. "
            "It is based on available account metadata such as account age, repeat posting, burstiness, "
            "and unusual follow/following ratios."
        ),
        "features": {
            "followers": followers,
            "following": following,
            "account_age_days": account_age_days,
            "post_count_7d": post_count_7d,
            "repetition_score": repetition_score,
            "burstiness": burstiness,
            "follower_following_ratio": round(ratio, 4),
        },
    }


def analyze_accounts(accounts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [analyze_account(account) for account in accounts]
