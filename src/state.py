"""Persistence layer for trace grades — Polars + CSV."""

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

SCHEMA = {
    "trace_id": pl.Utf8,
    "grade": pl.Utf8,
    "comment": pl.Utf8,
    "graded_at": pl.Utf8,
}


def load_grades(path: str | Path) -> pl.DataFrame:
    """Load grades CSV, returning an empty DataFrame if the file doesn't exist."""
    path = Path(path)
    if path.exists() and path.stat().st_size > 0:
        return pl.read_csv(path, schema=SCHEMA)
    return pl.DataFrame(schema=SCHEMA)


def save_grade(
    path: str | Path,
    trace_id: str,
    grade: str,
    comment: str = "",
) -> pl.DataFrame:
    """Upsert a grade for *trace_id* into the CSV at *path* and return the
    updated DataFrame."""
    path = Path(path)
    df = load_grades(path)
    now = datetime.now(timezone.utc).isoformat()

    new_row = pl.DataFrame(
        {
            "trace_id": [trace_id],
            "grade": [grade],
            "comment": [comment],
            "graded_at": [now],
        },
        schema=SCHEMA,
    )

    # Remove existing entry for this trace, then append the new one
    df = df.filter(pl.col("trace_id") != trace_id)
    df = pl.concat([df, new_row])
    df.write_csv(path)
    return df


def get_progress(df: pl.DataFrame) -> dict:
    """Return grading progress counts."""
    total = df.height
    graded = df.filter(pl.col("grade").is_not_null() & (pl.col("grade") != "")).height
    passed = df.filter(pl.col("grade") == "pass").height
    failed = df.filter(pl.col("grade") == "fail").height
    return {
        "total": total,
        "graded": graded,
        "passed": passed,
        "failed": failed,
        "ungraded": total - graded,
    }
