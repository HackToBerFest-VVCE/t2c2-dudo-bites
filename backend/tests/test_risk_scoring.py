from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.services.bot_classifier import build_bot_classifier
from backend.app.services.claim_analysis import analyze_claim
from backend.app.services.coordination_service import detect_coordination
from backend.app.services.data_validation import validate_post_dataframe
from backend.app.services.risk_scoring_service import explain_risk_score

BASE_DIR = Path(__file__).resolve().parents[2]
SAMPLE_POSTS_PATH = BASE_DIR / "data" / "sample" / "posts.csv"
SAMPLE_ACCOUNTS_PATH = BASE_DIR / "data" / "sample" / "accounts.csv"

app = FastAPI(title="DuoBites API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    posts: List[PostInput]
    accounts: List[AccountInput] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    posts_analyzed: int
    bot_predictions: List[Dict[str, Any]]
    claim_results: List[Dict[str, Any]]
    coordination_results: List[Dict[str, Any]]
    risk_summary: Dict[str, Any]


def load_sample_dataset() -> Dict[str, Any]:
    posts_df = pd.read_csv(SAMPLE_POSTS_PATH)
    accounts_df = pd.read_csv(SAMPLE_ACCOUNTS_PATH)
    return {"posts": posts_df.to_dict(orient="records"), "accounts": accounts_df.to_dict(orient="records")}


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "DuoBites"}


@app.get("/api/v1/sample-data")
def get_sample_data() -> Dict[str, Any]:
    return load_sample_dataset()


@app.post("/api/v1/ingest/csv")
async def ingest_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    content = await file.read()
    try:
        csv_io = io.StringIO(content.decode("utf-8"))
        df = pd.read_csv(csv_io)
        cleaned = validate_post_dataframe(df)
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="The CSV file is not valid UTF-8.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "accepted",
        "records": len(cleaned),
        "columns": cleaned.columns.tolist(),
        "message": "CSV was validated and accepted for analysis.",
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    if not request.posts:
        raise HTTPException(status_code=400, detail="No posts were provided for analysis.")

    posts = [
        {
            "account_id": post.account_id,
            "timestamp": pd.to_datetime(post.timestamp),
            "text": post.text,
        }
        for post in request.posts
    ]

    accounts = [
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

    if not accounts:
        accounts = [
            {
                "account_id": post["account_id"],
                "followers": 500,
                "following": 400,
                "account_age_days": 30,
                "post_count_7d": 4,
                "repetition_score": 0.2,
                "burstiness": 0.2,
            }
            for post in posts
        ]

    classifier = build_bot_classifier()
    bot_predictions = [classifier.predict_account(account) for account in accounts]
    claim_results = [analyze_claim(post["text"]) for post in posts]
    coordination_results = detect_coordination(posts)
    risk_summary = explain_risk_score(bot_predictions, claim_results, coordination_results)

    return AnalysisResponse(
        posts_analyzed=len(posts),
        bot_predictions=bot_predictions,
        claim_results=claim_results,
        coordination_results=coordination_results,
        risk_summary=risk_summary,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", reload=True)
