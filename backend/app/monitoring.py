from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "monitoring.db"


class SourceAdapter:
    name = "base"

    def fetch(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class SampleDataAdapter(SourceAdapter):
    name = "sample-data"

    def __init__(self, sample_path: str | Path):
        self.sample_path = Path(sample_path)

    def fetch(self) -> list[dict[str, Any]]:
        if not self.sample_path.exists():
            return []
        df = pd.read_csv(self.sample_path)
        return df.to_dict(orient="records")


class AlertStore:
    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    details TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'new',
                    created_at TEXT NOT NULL
                )
                """
            )

    def create_alert(self, source: str, title: str, summary: str, details: dict[str, Any]) -> dict[str, Any] | None:
        details_json = json.dumps(details, sort_keys=True)
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM alerts WHERE source=? AND title=? AND summary=? AND details=?",
                (source, title, summary, details_json),
            ).fetchone()
            if existing is not None:
                return None

            created_at = datetime.now(timezone.utc).isoformat()
            cursor = conn.execute(
                """
                INSERT INTO alerts (source, title, summary, details, state, created_at)
                VALUES (?, ?, ?, ?, 'new', ?)
                """,
                (source, title, summary, details_json, created_at),
            )
            alert_id = cursor.lastrowid
            return {
                "id": alert_id,
                "source": source,
                "title": title,
                "summary": summary,
                "details": details,
                "state": "new",
                "created_at": created_at,
            }

    def list_alerts(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, source, title, summary, details, state, created_at FROM alerts ORDER BY id DESC"
            ).fetchall()

        alerts = []
        for row in rows:
            alerts.append(
                {
                    "id": row["id"],
                    "source": row["source"],
                    "title": row["title"],
                    "summary": row["summary"],
                    "details": json.loads(row["details"]),
                    "state": row["state"],
                    "created_at": row["created_at"],
                }
            )
        return alerts

    def update_status(self, alert_id: int, new_state: str) -> bool:
        allowed = {"new", "reviewed", "dismissed", "resolved"}
        if new_state not in allowed:
            raise ValueError("State must be one of: new, reviewed, dismissed, resolved")

        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE alerts SET state = ? WHERE id = ?",
                (new_state, alert_id),
            )
        return cursor.rowcount > 0


class MonitoringService:
    def __init__(self, adapter: SourceAdapter, store: AlertStore):
        self.adapter = adapter
        self.store = store

    def run_once(self) -> list[dict[str, Any]]:
        items = self.adapter.fetch()
        created_alerts = []

        for item in items:
            text = str(item.get("text", "")).strip()
            account_id = str(item.get("account_id", "")).strip()
            if not text or not account_id:
                continue

            title = "Repeated content alert"
            summary = f"Repeated content detected for account {account_id}."
            details = {
                "account_id": account_id,
                "text": text,
                "timestamp": str(item.get("timestamp", "")),
                "source": self.adapter.name,
            }
            created = self.store.create_alert(self.adapter.name, title, summary, details)
            if created:
                created_alerts.append(created)

        return created_alerts


class DemoMonitorAdapter(SourceAdapter):
    name = "demo-monitor"

    def __init__(self, payload: list[dict[str, Any]]):
        self.payload = payload

    def fetch(self) -> list[dict[str, Any]]:
        return self.payload


if __name__ == "__main__":
    store = AlertStore(Path("data/monitoring.db"))
    demo = DemoMonitorAdapter([
        {
            "account_id": "user_101",
            "timestamp": "2026-10-24 10:00:00",
            "text": "Example claim about a public policy",
        }
    ])
    print(MonitoringService(adapter=demo, store=store).run_once())
