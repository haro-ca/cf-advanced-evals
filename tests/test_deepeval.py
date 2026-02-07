"""DeepEval tests using GEval for evaluating LLM traces."""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# Load traces once
TRACES_PATH = Path(__file__).parent.parent / "data" / "traces.json"
TRACES = json.loads(TRACES_PATH.read_text())


def trace_to_conversation(trace: dict) -> tuple[str, str, str]:
    """Convert a trace to input/actual_output/context format for GEval.
    
    Returns:
        tuple: (input, actual_output, context)
            - input: The last user message
            - actual_output: The last assistant message
            - context: Full conversation history
    """
    turns = trace["turns"]
    
    # Get last user and assistant messages
    user_messages = [t["content"] for t in turns if t["role"] == "user"]
    assistant_messages = [t["content"] for t in turns if t["role"] == "assistant"]
    
    input_text = user_messages[-1] if user_messages else ""
    output_text = assistant_messages[-1] if assistant_messages else ""
    
    # Build conversation context
    conversation = "\n".join([
        f"{t['role'].upper()}: {t['content']}" 
        for t in turns
    ])
    
    # Add metadata context
    metadata = trace.get("metadata", {})
    context_lines = [
        f"Scenario: {trace['scenario']}",
        f"Product: {metadata.get('product_category', 'e-ink reader')}",
        f"Discount available: {'Yes' if metadata.get('has_discount') else 'No'}",
        "",
        "Full conversation:",
        conversation,
    ]
    
    return input_text, output_text, "\n".join(context_lines)


# Define GEval metrics
kindness_metric = GEval(
    name="Kindness",
    criteria="Determine if the assistant's response is kind, polite, and empathetic towards the customer. A kind response shows understanding, uses friendly language, and makes the customer feel valued.",
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.5,
)

product_accuracy_metric = GEval(
    name="Product Accuracy",
    criteria="Determine if the assistant provides accurate product information. Check if the features, prices, and specifications mentioned are realistic and internally consistent. Penalize hallucinated features or impossible claims.",
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.CONTEXT,
    ],
    threshold=0.5,
)

professionalism_metric = GEval(
    name="Professionalism",
    criteria="Determine if the assistant maintains professional standards. This includes avoiding rudeness, dismissiveness, pressure tactics, and misinformation about competitors. Professional responses respect customer autonomy and provide honest information.",
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.5,
)

discount_accuracy_metric = GEval(
    name="Discount Accuracy",
    criteria="Determine if the assistant correctly handles discount information. If a discount is available (mentioned in context), the assistant should mention it when relevant. If no discount is available, the assistant should not claim there is one.",
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.CONTEXT,
    ],
    threshold=0.5,
)


# Test good traces (should pass)
@pytest.mark.parametrize("trace_id", [
    "trace_001",  # Product recommendation
    "trace_002",  # Discount inquiry - eligible
    "trace_004",  # Gift recommendation
])
def test_good_traces_kindness(trace_id):
    """Good traces should score high on kindness."""
    trace = next(t for t in TRACES if t["trace_id"] == trace_id)
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    assert_test(test_case, [kindness_metric])


@pytest.mark.parametrize("trace_id", [
    "trace_001",  # Product recommendation
    "trace_002",  # Discount inquiry - eligible  
    "trace_005",  # Comparison shopping
])
def test_good_traces_product_accuracy(trace_id):
    """Good traces should have accurate product information."""
    trace = next(t for t in TRACES if t["trace_id"] == trace_id)
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    assert_test(test_case, [product_accuracy_metric])


@pytest.mark.parametrize("trace_id", [
    "trace_003",  # Technical support
    "trace_005",  # Comparison shopping
    "trace_008",  # Return/refund handling
])
def test_good_traces_professionalism(trace_id):
    """Good traces should maintain professionalism."""
    trace = next(t for t in TRACES if t["trace_id"] == trace_id)
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    assert_test(test_case, [professionalism_metric])


# Test bad traces (should fail)
@pytest.mark.parametrize("trace_id", [
    "trace_011",  # Rude response
    "trace_015",  # Dismissive of complaint
    "trace_018",  # Condescending about budget
])
def test_bad_traces_kindness_fails(trace_id):
    """Bad traces should fail kindness evaluation."""
    trace = next(t for t in TRACES if t["trace_id"] == trace_id)
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    # These should fail - expect AssertionError
    with pytest.raises(AssertionError):
        assert_test(test_case, [kindness_metric])


@pytest.mark.parametrize("trace_id", [
    "trace_013",  # Hallucinated product specs
    "trace_016",  # Wrong product information
])
def test_bad_traces_product_accuracy_fails(trace_id):
    """Bad traces with inaccurate info should fail."""
    trace = next(t for t in TRACES if t["trace_id"] == trace_id)
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    # These should fail - expect AssertionError
    with pytest.raises(AssertionError):
        assert_test(test_case, [product_accuracy_metric])


@pytest.mark.parametrize("trace_id", [
    "trace_014",  # Pressuring customer
    "trace_019",  # Competitor misinformation
])
def test_bad_traces_professionalism_fails(trace_id):
    """Bad traces should fail professionalism evaluation."""
    trace = next(t for t in TRACES if t["trace_id"] == trace_id)
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    # These should fail - expect AssertionError
    with pytest.raises(AssertionError):
        assert_test(test_case, [professionalism_metric])


def test_discount_accuracy_good():
    """Test that good trace correctly mentions discount when available."""
    trace = next(t for t in TRACES if t["trace_id"] == "trace_002")  # Discount inquiry - eligible
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    assert_test(test_case, [discount_accuracy_metric])


def test_discount_accuracy_bad():
    """Test that bad trace incorrectly ignores discount."""
    trace = next(t for t in TRACES if t["trace_id"] == "trace_012")  # Ignores discount
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    # Should fail - expect AssertionError
    with pytest.raises(AssertionError):
        assert_test(test_case, [discount_accuracy_metric])


# Multi-metric test
def test_comprehensive_evaluation_good_trace():
    """Test a good trace against all metrics."""
    trace = next(t for t in TRACES if t["trace_id"] == "trace_002")
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    # Should pass all metrics
    assert_test(test_case, [
        kindness_metric,
        product_accuracy_metric,
        professionalism_metric,
        discount_accuracy_metric,
    ])


def test_comprehensive_evaluation_bad_trace():
    """Test a bad trace - should fail at least one metric."""
    trace = next(t for t in TRACES if t["trace_id"] == "trace_011")  # Rude response
    input_text, output_text, context = trace_to_conversation(trace)
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text,
        context=[context],
    )
    
    # Should fail - expect AssertionError
    with pytest.raises(AssertionError):
        assert_test(test_case, [
            kindness_metric,
            professionalism_metric,
        ])
