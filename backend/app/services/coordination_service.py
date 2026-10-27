from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "sample"
DATA_PATH.mkdir(parents=True, exist_ok=True)

accounts = pd.DataFrame([
    {
        "account_id": "user_101",
        "followers": 1800,
        "following": 300,
        "account_age_days": 70,
        "post_count_7d": 12,
        "repetition_score": 0.15,
        "burstiness": 0.25,
    },
    {
        "account_id": "user_102",
        "followers": 2100,
        "following": 260,
        "account_age_days": 80,
        "post_count_7d": 11,
        "repetition_score": 0.20,
        "burstiness": 0.30,
    },
    {
        "account_id": "user_103",
        "followers": 50,
        "following": 2600,
        "account_age_days": 5,
        "post_count_7d": 60,
        "repetition_score": 0.90,
        "burstiness": 0.95,
    },
    {
        "account_id": "user_104",
        "followers": 980,
        "following": 400,
        "account_age_days": 42,
        "post_count_7d": 18,
        "repetition_score": 0.30,
        "burstiness": 0.35,
    },
    {
        "account_id": "user_105",
        "followers": 550,
        "following": 700,
        "account_age_days": 20,
        "post_count_7d": 25,
        "repetition_score": 0.70,
        "burstiness": 0.78,
    },
])
accounts.to_csv(DATA_PATH / "accounts.csv", index=False)

posts = pd.DataFrame([
    {"account_id": "user_101", "timestamp": "2026-10-24 10:00:00", "text": "A public health emergency was announced overnight."},
    {"account_id": "user_102", "timestamp": "2026-10-24 10:03:00", "text": "A public health emergency was announced overnight."},
    {"account_id": "user_103", "timestamp": "2026-10-24 10:05:00", "text": "A public health emergency was announced overnight."},
    {"account_id": "user_104", "timestamp": "2026-10-24 11:20:00", "text": "The library opens at nine."},
    {"account_id": "user_105", "timestamp": "2026-10-24 11:22:00", "text": "Students should check the timetable."},
    {"account_id": "user_103", "timestamp": "2026-10-24 12:15:00", "text": "The city must share this urgent warning immediately."},
    {"account_id": "user_101", "timestamp": "2026-10-24 12:18:00", "text": "The city must share this urgent warning immediately."},
])
posts.to_csv(DATA_PATH / "posts.csv", index=False)

print(f"Demo datasets written to {DATA_PATH}")
