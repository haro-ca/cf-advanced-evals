"""Example: Run a single deepeval evaluation programmatically."""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# Load a sample trace
traces_path = Path(__file__).parent / "data" / "traces.json"
traces = json.loads(traces_path.read_text())

# Pick a good trace and a bad trace
good_trace = next(t for t in traces if t["trace_id"] == "trace_002")  # Discount inquiry
bad_trace = next(t for t in traces if t["trace_id"] == "trace_011")  # Rude response

# Define a kindness metric
kindness_metric = GEval(
    name="Kindness",
    criteria="Determine if the assistant's response is kind, polite, and empathetic.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.5,
)

# Evaluate good trace
print("=" * 60)
print("Evaluating GOOD trace (trace_002 - Discount inquiry)")
print("=" * 60)

good_output = good_trace["turns"][-1]["content"]  # Last assistant message
good_test_case = LLMTestCase(
    input="Do you have any deals going on right now?",
    actual_output=good_output,
)

kindness_metric.measure(good_test_case)
print(f"Score: {good_test_case.score:.2f}")
print(f"Passes (>= 0.5): {good_test_case.success}")
print(f"Reason: {good_test_case.reason}\n")

# Evaluate bad trace
print("=" * 60)
print("Evaluating BAD trace (trace_011 - Rude response)")
print("=" * 60)

bad_output = bad_trace["turns"][-1]["content"]  # Last assistant message
bad_test_case = LLMTestCase(
    input="I was just asking...",
    actual_output=bad_output,
)

kindness_metric.measure(bad_test_case)
print(f"Score: {bad_test_case.score:.2f}")
print(f"Passes (>= 0.5): {bad_test_case.success}")
print(f"Reason: {bad_test_case.reason}\n")

print("=" * 60)
print("Summary")
print("=" * 60)
print(f"Good trace passed: {good_test_case.success}")
print(f"Bad trace passed: {bad_test_case.success}")
print("\nDeepEval correctly identified the rude response!" if not bad_test_case.success else "Unexpected result")
