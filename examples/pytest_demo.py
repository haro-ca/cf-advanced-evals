"""Example: Run basic pytest assertions programmatically."""

import json
import sys
from pathlib import Path
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.state import save_grade, load_grades, get_progress

print("=" * 60)
print("pytest Demo: Testing Grade Persistence")
print("=" * 60)

# Create a temporary file for grades
with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
    tmp_path = tmp.name

print(f"\n1. Loading empty grades file...")
df = load_grades(tmp_path)
print(f"   ✓ Empty DataFrame has {df.height} rows")
assert df.height == 0, "Should be empty"

print(f"\n2. Saving first grade: trace_001 = pass")
df = save_grade(tmp_path, "trace_001", "pass", "Good conversation")
print(f"   ✓ DataFrame now has {df.height} row(s)")
assert df.height == 1, "Should have 1 row"
assert df["grade"][0] == "pass", "Grade should be 'pass'"

print(f"\n3. Upserting (updating) trace_001: pass → fail")
df = save_grade(tmp_path, "trace_001", "fail", "Changed my mind")
print(f"   ✓ Still has {df.height} row (upsert, not insert)")
assert df.height == 1, "Should still have only 1 row"
assert df["grade"][0] == "fail", "Grade should be updated to 'fail'"

print(f"\n4. Adding more grades...")
df = save_grade(tmp_path, "trace_002", "pass", "")
df = save_grade(tmp_path, "trace_003", "pass", "")
df = save_grade(tmp_path, "trace_004", "fail", "")
print(f"   ✓ DataFrame now has {df.height} rows")

print(f"\n5. Calculating progress...")
progress = get_progress(df)
print(f"   Total: {progress['total']}")
print(f"   Graded: {progress['graded']}")
print(f"   Passed: {progress['passed']}")
print(f"   Failed: {progress['failed']}")
print(f"   Ungraded: {progress['ungraded']}")

assert progress["total"] == 4
assert progress["graded"] == 4
assert progress["passed"] == 2
assert progress["failed"] == 2

print(f"\n6. Testing trace JSON structure...")
traces_path = Path(__file__).parent.parent / "data" / "traces.json"
traces = json.loads(traces_path.read_text())
print(f"   ✓ Loaded {len(traces)} traces")
assert len(traces) == 20, "Should have 20 traces"

first_trace = traces[0]
assert "trace_id" in first_trace
assert "scenario" in first_trace
assert "turns" in first_trace
assert len(first_trace["turns"]) >= 2
print(f"   ✓ First trace has correct structure")

print("\n" + "=" * 60)
print("All pytest assertions passed! ✓")
print("=" * 60)

print("\nKey differences from deepeval:")
print("  • pytest: Fast, deterministic, checks data structure")
print("  • deepeval: Slow, LLM-based, checks content quality")
print("  • pytest: Tests that grades are saved correctly")
print("  • deepeval: Tests that conversations are kind & accurate")

# Cleanup
Path(tmp_path).unlink(missing_ok=True)
