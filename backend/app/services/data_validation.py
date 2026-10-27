import math
from typing import Dict, List

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class BotBehaviorClassifier:
    """Baseline scikit-learn bot detector.

    This is intentionally lightweight and designed for a transparent MVP.
    It does not prove bot membership; it only estimates suspicious behavior.
    """

    def __init__(self):
        self.model = self._build_model()

    def _build_model(self):
        training_data = [
            {"followers": 300, "following": 1200, "account_age_days": 10, "post_count_7d": 60, "repetition_score": 0.8, "burstiness": 0.9},
            {"followers": 1500, "following": 200, "account_age_days": 90, "post_count_7d": 15, "repetition_score": 0.2, "burstiness": 0.3},
            {"followers": 50, "following": 2000, "account_age_days": 3, "post_count_7d": 80, "repetition_score": 0.9, "burstiness": 0.95},
            {"followers": 1200, "following": 180, "account_age_days": 120, "post_count_7d": 10, "repetition_score": 0.1, "burstiness": 0.2},
            {"followers": 220, "following": 700, "account_age_days": 14, "post_count_7d": 45, "repetition_score": 0.7, "burstiness": 0.8},
            {"followers": 800, "following": 300, "account_age_days": 70, "post_count_7d": 18, "repetition_score": 0.2, "burstiness": 0.3},
            {"followers": 80, "following": 3500, "account_age_days": 5, "post_count_7d": 100, "repetition_score": 0.95, "burstiness": 0.9},
            {"followers": 2500, "following": 250, "account_age_days": 180, "post_count_7d": 12, "repetition_score": 0.1, "burstiness": 0.2},
        ]
        labels = [1, 0, 1, 0, 1, 0, 1, 0]

        vectorizer = DictVectorizer(sparse=False)
        X = vectorizer.fit_transform(training_data)
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000)),
        ])
        model.fit(X, labels)
        self.vectorizer = vectorizer
        return model

    def _to_feature_dict(self, account: Dict) -> Dict:
        followers = float(account.get("followers", 0) or 0)
        following = float(account.get("following", 0) or 0)
        account_age_days = float(account.get("account_age_days", 0) or 0)
        post_count_7d = float(account.get("post_count_7d", 0) or 0)
        repetition_score = float(account.get("repetition_score", 0.0) or 0.0)
        burstiness = float(account.get("burstiness", 0.0) or 0.0)

        ratio = followers / max(following, 1)
        return {
            "followers": followers,
            "following": following,
            "account_age_days": account_age_days,
            "post_count_7d": post_count_7d,
            "repetition_score": repetition_score,
            "burstiness": burstiness,
            "follower_following_ratio": ratio,
        }

    def predict_account(self, account: Dict) -> Dict:
        feature_dict = self._to_feature_dict(account)
        x = self.vectorizer.transform([feature_dict])
        probability = self.model.predict_proba(x)[0][1]
        score = round(float(probability) * 100, 2)

        if score >= 70:
            label = "Likely suspicious"
            explanation = "The account shows strong bot-like behavior patterns, including aggressive posting cadence or atypical follow/follower ratios."
        elif score >= 45:
            label = "Needs review"
            explanation = "The profile is moderately unusual, but more evidence is required before concluding bot behavior."
        else:
            label = "Low suspicion"
            explanation = "The current signals do not strongly indicate bot-like behavior."

        return {
            "account_id": account.get("account_id", "unknown"),
            "bot_probability": score,
            "bot_label": label,
            "reason": explanation,
            "features": feature_dict,
        }


def build_bot_classifier() -> BotBehaviorClassifier:
    return BotBehaviorClassifier()
