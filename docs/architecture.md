import pandas as pd
import pytest

from backend.app.services.data_validation import validate_post_dataframe


def test_missing_columns_raises_value_error():
    df = pd.DataFrame({"account_id": ["u1"], "text": ["hello"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_post_dataframe(df)


def test_empty_dataframe_raises_value_error():
    df = pd.DataFrame(columns=["account_id", "timestamp", "text"])

    with pytest.raises(ValueError, match="The dataset is empty"):
        validate_post_dataframe(df)


def test_invalid_timestamp_raises_value_error():
    df = pd.DataFrame({
        "account_id": ["u1"],
        "timestamp": ["not-a-date"],
        "text": ["example claim"],
    })

    with pytest.raises(ValueError, match="invalid"):
        validate_post_dataframe(df)


def test_valid_dataframe_is_returned_cleanly():
    df = pd.DataFrame({
        "account_id": ["u1", "u2"],
        "timestamp": ["2026-10-24 10:00:00", "2026-10-24 10:04:00"],
        "text": ["example claim", "example claim"],
    })

    cleaned = validate_post_dataframe(df)

    assert len(cleaned) == 2
    assert cleaned["timestamp"].dtype.kind in {"M", "m"}
