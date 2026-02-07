# cf-advanced-evals

A Streamlit-based data viewer for grading LLM conversation traces. Built for evaluating an e-ink reader sales assistant, with support for pass/fail grading, optional comments, and persistent state.

## Setup

```bash
# Install dependencies (uses uv)
uv sync
```

## Generate sample data

```bash
uv run python data/generate_traces.py
```

This creates `data/traces.json` with 20 multi-turn conversations (10 good, 10 bad).

## Run the app

```bash
uv run streamlit run app.py
```

## Run tests

### pytest (basic tests)
```bash
uv run pytest tests/test_basic.py -v
```

Tests data structure, grade persistence, and trace JSON schema. Fast and deterministic.

### deepeval (LLM-based evaluation)
```bash
# Requires OPENAI_API_KEY
export OPENAI_API_KEY="your-api-key"
uv run pytest tests/test_deepeval.py -v
```

Uses GEval metrics to evaluate conversation quality (kindness, accuracy, professionalism). See [tests/README.md](tests/README.md) for details.

**Note**: DeepEval imports may be slow on WSL/Windows filesystems. Set `PYTHONDONTWRITEBYTECODE=1` or move project to native Linux filesystem for better performance.

## Testing comparison: pytest vs deepeval

| | pytest | deepeval |
|---|---|---|
| **Tests** | 8 tests | 19 tests |
| **Speed** | ~9 seconds | Slower (requires LLM calls) |
| **Cost** | Free | Requires OpenAI API credits |
| **Deterministic** | ✅ Yes | ❌ No (LLM-based) |
| **Evaluates** | Data structure | Content quality |

**pytest** validates that grades are saved correctly and traces have the right structure.  
**deepeval** uses an LLM to judge if conversations are kind, accurate, and professional.

## Examples

Run the demo scripts to see testing in action:

```bash
# pytest demo - fast, deterministic testing
uv run python examples/pytest_demo.py

# deepeval demo - LLM-based evaluation (requires OPENAI_API_KEY)
export OPENAI_API_KEY="your-api-key"
uv run python examples/deepeval_demo.py
```

## Project structure

```
app.py                   # Streamlit entry point
src/
  state.py               # Grade persistence (Polars + CSV)
data/
  generate_traces.py     # Script to create sample traces
  traces.json            # 20 sample multi-turn conversations
  grades.csv             # Created at runtime — stores grading state
tests/
  test_basic.py          # pytest: data structure tests
  test_deepeval.py       # DeepEval: LLM-based quality metrics (GEval)
  README.md              # Detailed testing documentation
examples/
  pytest_demo.py         # Interactive pytest demonstration
  deepeval_demo.py       # Interactive deepeval demonstration
```

## Features

- Chat-style display of multi-turn LLM conversations
- Pass / Fail grading buttons with optional comments
- Sidebar navigation with color-coded grading status
- Progress tracking (graded / total, pass / fail counts)
- Persistent state saved to CSV via Polars
