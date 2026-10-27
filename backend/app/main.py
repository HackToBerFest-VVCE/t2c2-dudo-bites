from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.app.services.bot_classifier import analyze_accounts
from backend.app.services.claim_analysis import analyze_claims
from backend.app.services.coordination_service import detect_coordination
from backend.app.services.data_validation import validate_post_dataframe
from backend.app.services.risk_scoring_service import explain_risk_score

BASE_DIR = Path(__file__).resolve().parents[2]
SAMPLE_POSTS_PATH = BASE_DIR / "data" / "sample" / "posts.csv"
SAMPLE_ACCOUNTS_PATH = BASE_DIR / "data" / "sample" / "accounts.csv"

app = FastAPI(
    title="DuoBites API",
    version="0.1.0",
    description="Bot-driven misinformation detection MVP for DuoBites.",
)


class AccountInput(BaseModel):
    account_id: str
    followers: int | None = 0
    following: int | None = 0
    account_age_days: int | None = 0
    post_count_7d: int | None = 0
    repetition_score: float | None = 0.0
    burstiness: float | None = 0.0


class PostInput(BaseModel):
    account_id: str
    timestamp: str
    text: str


class AnalysisRequest(BaseModel):
    posts: list[PostInput]
    accounts: list[AccountInput] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    posts_analyzed: int
    bot_predictions: list[dict[str, Any]]
    claim_results: list[dict[str, Any]]
    coordination_results: list[dict[str, Any]]
    risk_summary: dict[str, Any]


def load_sample_dataset() -> dict[str, Any]:
    posts_df = pd.read_csv(SAMPLE_POSTS_PATH)
    accounts_df = pd.read_csv(SAMPLE_ACCOUNTS_PATH)
    return {
        "posts": posts_df.to_dict(orient="records"),
        "accounts": accounts_df.to_dict(orient="records"),
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "DuoBites",
        "stage": "mvp",
    }


@app.get("/api/v1/sample-data")
def get_sample_data() -> dict[str, Any]:
    return load_sample_dataset()


@app.post("/api/v1/ingest/csv")
async def ingest_csv(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploaded.")
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    file_data = await file.read()
    if not file_data:
        raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")
    if len(file_data) > 2_000_000:
        raise HTTPException(status_code=413, detail="Uploaded CSV exceeds the 2 MB file-size limit.")

    try:
        csv_buffer = io.StringIO(file_data.decode("utf-8"))
        raw_df = pd.read_csv(csv_buffer)
        cleaned_df = validate_post_dataframe(raw_df)
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="The CSV file is not valid UTF-8.") from exc
    except pd.errors.EmptyDataError as exc:
        raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.") from exc
    except pd.errors.ParserError as exc:
        raise HTTPException(status_code=400, detail="The CSV file is malformed and could not be parsed.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to parse CSV: {exc}") from exc

    return {
        "status": "accepted",
        "rows": len(cleaned_df),
        "columns": cleaned_df.columns.tolist(),
        "message": "CSV was validated and accepted for analysis.",
    }


@app.post("/api/v1/ingest/json")
async def ingest_json(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploaded.")
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported.")

    file_data = await file.read()
    if not file_data:
        raise HTTPException(status_code=400, detail="The uploaded JSON file is empty.")
    if len(file_data) > 2_000_000:
        raise HTTPException(status_code=413, detail="Uploaded JSON exceeds the 2 MB file-size limit.")

    try:
        import json
        payload = json.loads(file_data.decode("utf-8"))
        if not isinstance(payload, dict) or "posts" not in payload:
            raise ValueError("JSON payload must contain a 'posts' list.")
        rows = [
            {
                "account_id": str(item["account_id"]).strip(),
                "timestamp": str(item["timestamp"]).strip(),
                "text": str(item["text"]).strip(),
            }
            for item in payload["posts"]
        ]
        df = pd.DataFrame(rows)
        cleaned_df = validate_post_dataframe(df)
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="The JSON file is not valid UTF-8.") from exc

    return {
        "status": "accepted",
        "rows": len(cleaned_df),
        "columns": cleaned_df.columns.tolist(),
        "message": "JSON was validated and accepted for analysis.",
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    if not request.posts:
        raise HTTPException(status_code=400, detail="No posts were provided for analysis.")

    post_records = [
        {
            "account_id": post.account_id,
            "timestamp": pd.to_datetime(post.timestamp),
            "text": post.text,
        }
        for post in request.posts
    ]

    account_records = [
        {
            "account_id": account.account_id,
            "followers": account.followers or 0,
            "following": account.following or 0,
            "account_age_days": account.account_age_days or 0,
            "post_count_7d": account.post_count_7d or 0,
            "repetition_score": account.repetition_score or 0.0,
            "burstiness": account.burstiness or 0.0,
        }
        for account in request.accounts
    ]

    bot_predictions = analyze_accounts(account_records) if account_records else []
    claim_results = analyze_claims(post_records)
    coordination_results = detect_coordination(post_records)
    risk_summary = explain_risk_score(bot_predictions, claim_results, coordination_results)

    return AnalysisResponse(
        posts_analyzed=len(post_records),
        bot_predictions=bot_predictions,
        claim_results=claim_results,
        coordination_results=coordination_results,
        risk_summary=risk_summary,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
