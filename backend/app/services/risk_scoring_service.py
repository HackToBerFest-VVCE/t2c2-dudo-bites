import re
from collections import defaultdict
from datetime import timedelta
from typing import Dict, List

import networkx as nx


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_coordination(posts: List[Dict], time_window_minutes: int = 10) -> List[Dict]:
    grouped = defaultdict(list)
    for post in posts:
        normalized = normalize_text(post.get("text", ""))
        if normalized:
            grouped[normalized].append(post)

    results: List[Dict] = []
    for normalized_text, group in grouped.items():
        accounts = sorted({post["account_id"] for post in group})
        if len(accounts) < 2:
            continue

        timestamps = [post["timestamp"] for post in group]
        first_seen = min(timestamps)
        last_seen = max(timestamps)
        elapsed_minutes = round((last_seen - first_seen).total_seconds() / 60, 2)

        in_window = []
        for post in group:
            delta = post["timestamp"] - first_seen
            if delta <= timedelta(minutes=time_window_minutes):
                in_window.append(post)

        suspicious_accounts = sorted({post["account_id"] for post in in_window})
        if len(suspicious_accounts) < 2:
            continue

        graph = nx.Graph()
        graph.add_nodes_from(suspicious_accounts)
        for account_id in suspicious_accounts:
            graph.add_edge(account_id, account_id)

        results.append({
            "group_label": normalized_text[:80],
            "accounts": suspicious_accounts,
            "account_count": len(suspicious_accounts),
            "first_seen": first_seen.isoformat(),
            "last_seen": last_seen.isoformat(),
            "time_span_minutes": elapsed_minutes,
            "network_nodes": graph.number_of_nodes(),
            "reason": "Similar text appears across multiple accounts within a short time window; this suggests potential coordination requiring human review.",
        })

    return results
