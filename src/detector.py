
import csv
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

WINDOW_MINUTES = 10


def normalize(text):
    text = text.lower().strip()
    return re.sub(r"[^\w\s]", "", text)


def detect_campaigns(posts):
    groups = defaultdict(list)

    for post in posts:
        text = normalize(post["text"])
        if text:
            groups[text].append(post)

    results = []

    for text, group in groups.items():
        group.sort(key=lambda p: p["timestamp"])

        for i, first in enumerate(group):
            matched = [
                post for post in group[i:]
                if (post["timestamp"] - first["timestamp"])
                .total_seconds() <= WINDOW_MINUTES * 60
            ]

            accounts = sorted({
                post["account_id"] for post in matched
            })

            if len(accounts) >= 2:
                result = {
                    "matched_text": text,
                    "accounts": ", ".join(accounts),
                    "account_count": len(accounts),
                    "first_seen": first["timestamp"].isoformat(
                        sep=" "
                    ),
                    "indicator": "Potential coordination"
                }

                if result not in results:
                    results.append(result)

    return results


def main():
    root = Path(__file__).resolve().parent.parent
    input_file = root / "data" / "sample_posts.csv"
    output_file = root / "coordination_report.csv"

    with input_file.open(
        newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        required = {"account_id", "timestamp", "text"}

        if not reader.fieldnames or not required.issubset(
            reader.fieldnames
        ):
            raise ValueError(
                "CSV needs account_id, timestamp and text columns"
            )

        posts = []

        for row in reader:
            posts.append({
                "account_id": row["account_id"].strip(),
                "timestamp": datetime.strptime(
                    row["timestamp"].strip(),
                    "%Y-%m-%d %H:%M:%S"
                ),
                "text": row["text"].strip()
            })

    results = detect_campaigns(posts)

    columns = [
        "matched_text", "accounts", "account_count",
        "first_seen", "indicator"
    ]

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)

    print(f"Posts analyzed: {len(posts)}")
    print(f"Potential coordination groups: {len(results)}")
    print(f"Report saved to: {output_file}")
    print("Coordination indicators require human review.")


if __name__ == "__main__":
    main()
