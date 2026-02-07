# DeepEval Tests

This directory contains DeepEval tests using GEval metrics for evaluating LLM traces.

## Setup

DeepEval requires an OpenAI API key (or other LLM provider) to run evaluations.

Set your API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## GEval Metrics

The tests use four custom GEval metrics:

### 1. Kindness
Evaluates if responses are polite, empathetic, and customer-friendly.
- **Threshold**: 0.5
- **Good examples**: trace_001, trace_002, trace_004
- **Bad examples**: trace_011 (rude), trace_015 (dismissive), trace_018 (condescending)

### 2. Product Accuracy
Checks for correct product information without hallucinations.
- **Threshold**: 0.5  
- **Good examples**: trace_001, trace_002, trace_005
- **Bad examples**: trace_013 (hallucinated specs), trace_016 (wrong info)

### 3. Professionalism
Ensures no rudeness, pressure tactics, or misinformation.
- **Threshold**: 0.5
- **Good examples**: trace_003, trace_005, trace_008
- **Bad examples**: trace_014 (pressure), trace_019 (competitor misinformation)

### 4. Discount Accuracy
Verifies correct handling of discount information.
- **Threshold**: 0.5
- **Good example**: trace_002 (mentions discount when available)
- **Bad example**: trace_012 (ignores discount)

## Running Tests

```bash
# Run all deepeval tests
uv run pytest tests/test_deepeval.py -v

# Run specific metric tests
uv run pytest tests/test_deepeval.py -k "kindness" -v

# Run tests that expect failures
uv run pytest tests/test_deepeval.py -k "fails" -v
```

### Performance Note (WSL/Windows)

If you're running on WSL with a Windows filesystem (`/mnt/c/...`), imports may be very slow due to filesystem performance. Workarounds:

```bash
# Option 1: Disable Python bytecode writing
PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_deepeval.py -v

# Option 2: Clone repo to native Linux filesystem (much faster)
cp -r /mnt/c/Users/.../project ~/project && cd ~/project
```

## Test Structure

**Good trace tests** - Should pass:
- 3 tests for kindness (parametrized)
- 3 tests for product accuracy (parametrized)
- 3 tests for professionalism (parametrized)
- 1 test for discount accuracy
- 1 comprehensive multi-metric test

**Bad trace tests** - Should raise AssertionError:
- 3 tests for kindness failures (parametrized)
- 2 tests for product accuracy failures (parametrized)
- 2 tests for professionalism failures (parametrized)
- 1 test for discount accuracy failure
- 1 comprehensive multi-metric test

**Total**: 19 tests

## Comparison: pytest vs deepeval

| Feature | pytest (test_basic.py) | deepeval (test_deepeval.py) |
|---------|------------------------|------------------------------|
| **Focus** | Data structure & logic | Content quality & semantics |
| **Evaluation** | Deterministic assertions | LLM-based judgment |
| **Speed** | Fast (<10s) | Slower (requires LLM calls) |
| **Cost** | Free | Requires API credits |
| **Use case** | Unit tests, data integrity | End-to-end quality checks |
| **False positives** | None (exact matching) | Possible (LLM variability) |

### When to use pytest
- Testing data persistence (grades CSV)
- Validating trace JSON structure
- Checking progress calculations
- Fast CI/CD checks

### When to use deepeval
- Evaluating conversation quality
- Detecting tone/politeness issues
- Finding hallucinated information
- Assessing customer experience
