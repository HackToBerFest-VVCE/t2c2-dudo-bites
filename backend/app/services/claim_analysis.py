import pandas as pd

REQUIRED_COLUMNS = {"account_id", "timestamp", "text"}


def validate_post_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("The dataset is empty.")

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    cleaned = df.copy()
    cleaned["account_id"] = cleaned["account_id"].fillna("").astype(str).str.strip()
    cleaned["text"] = cleaned["text"].fillna("").astype(str).str.strip()

    if (cleaned["account_id"] == "").any() or (cleaned["text"] == "").any():
        raise ValueError("Rows contain blank account_id or text values.")

    try:
        cleaned["timestamp"] = pd.to_datetime(cleaned["timestamp"], errors="raise")
    except Exception as exc:  # pragma: no cover - defensive guard
        raise ValueError("One or more timestamps are invalid.") from exc

    return cleaned
