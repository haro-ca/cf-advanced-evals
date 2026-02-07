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

## Project structure

```
app.py                   # Streamlit entry point
src/
  state.py               # Grade persistence (Polars + CSV)
data/
  generate_traces.py     # Script to create sample traces
  traces.json            # 20 sample multi-turn conversations
  grades.csv             # Created at runtime — stores grading state
```

## Features

- Chat-style display of multi-turn LLM conversations
- Pass / Fail grading buttons with optional comments
- Sidebar navigation with color-coded grading status
- Progress tracking (graded / total, pass / fail counts)
- Persistent state saved to CSV via Polars
