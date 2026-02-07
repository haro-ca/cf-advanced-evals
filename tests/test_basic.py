"""Basic pytest tests for the trace grading system."""

import json
import tempfile
from pathlib import Path

import pytest

from src.state import get_progress, load_grades, save_grade


def test_load_empty_grades():
    """Test loading grades from a non-existent file returns empty DataFrame."""
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        tmp_path = tmp.name
    
    df = load_grades(tmp_path)
    assert df.height == 0
    assert "trace_id" in df.columns
    assert "grade" in df.columns
    assert "comment" in df.columns


def test_save_grade():
    """Test saving a single grade."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp_path = tmp.name
    
    try:
        df = save_grade(tmp_path, "trace_001", "pass", "Good conversation")
        assert df.height == 1
        assert df["trace_id"][0] == "trace_001"
        assert df["grade"][0] == "pass"
        assert df["comment"][0] == "Good conversation"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_upsert_grade():
    """Test that saving a grade for the same trace_id replaces the old one."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp_path = tmp.name
    
    try:
        # Save initial grade
        df = save_grade(tmp_path, "trace_001", "pass", "Initial")
        assert df.height == 1
        
        # Upsert with new grade
        df = save_grade(tmp_path, "trace_001", "fail", "Changed mind")
        assert df.height == 1  # Still only 1 row
        assert df["grade"][0] == "fail"
        assert df["comment"][0] == "Changed mind"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_progress_calculation():
    """Test progress stats calculation."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp_path = tmp.name
    
    try:
        # Add multiple grades
        df = save_grade(tmp_path, "trace_001", "pass", "")
        df = save_grade(tmp_path, "trace_002", "fail", "")
        df = save_grade(tmp_path, "trace_003", "pass", "")
        
        progress = get_progress(df)
        assert progress["total"] == 3
        assert progress["graded"] == 3
        assert progress["passed"] == 2
        assert progress["failed"] == 1
        assert progress["ungraded"] == 0
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_load_traces_from_json():
    """Test that traces.json can be loaded and has expected structure."""
    traces_path = Path(__file__).parent.parent / "data" / "traces.json"
    
    assert traces_path.exists(), "traces.json should exist"
    
    traces = json.loads(traces_path.read_text())
    
    assert len(traces) == 20, "Should have 20 traces"
    
    # Check first trace has required fields
    first_trace = traces[0]
    assert "trace_id" in first_trace
    assert "scenario" in first_trace
    assert "metadata" in first_trace
    assert "turns" in first_trace
    
    # Check turns structure
    assert len(first_trace["turns"]) >= 2, "Should have at least 2 turns"
    assert first_trace["turns"][0]["role"] in ("user", "assistant")
    assert "content" in first_trace["turns"][0]


def test_good_vs_bad_traces():
    """Test that we have a mix of good and bad traces."""
    traces_path = Path(__file__).parent.parent / "data" / "traces.json"
    traces = json.loads(traces_path.read_text())
    
    # First 10 should be good, last 10 should be bad (based on trace_id)
    good_traces = [t for t in traces if t["trace_id"] <= "trace_010"]
    bad_traces = [t for t in traces if t["trace_id"] > "trace_010"]
    
    assert len(good_traces) == 10, "Should have 10 good traces"
    assert len(bad_traces) == 10, "Should have 10 bad traces"


@pytest.mark.parametrize("grade,expected", [
    ("pass", {"passed": 1, "failed": 0}),
    ("fail", {"passed": 0, "failed": 1}),
])
def test_grade_types(grade, expected):
    """Test different grade types are counted correctly."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp_path = tmp.name
    
    try:
        df = save_grade(tmp_path, "trace_001", grade, "")
        progress = get_progress(df)
        
        assert progress["passed"] == expected["passed"]
        assert progress["failed"] == expected["failed"]
    finally:
        Path(tmp_path).unlink(missing_ok=True)
