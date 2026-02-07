"""LLM Trace Grading Viewer — Streamlit app."""

import json
from pathlib import Path

import streamlit as st

from src.state import get_progress, load_grades, save_grade

# ── Paths ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
TRACES_PATH = ROOT / "data" / "traces.json"
GRADES_PATH = ROOT / "data" / "grades.csv"

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Trace Grader", page_icon="📝", layout="wide")


# ── Helpers ──────────────────────────────────────────────────────────────
@st.cache_data
def load_traces() -> list[dict]:
    return json.loads(TRACES_PATH.read_text())


def init_state():
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "grades_df" not in st.session_state:
        st.session_state.grades_df = load_grades(GRADES_PATH)


def grade_color(grade: str | None) -> str:
    if grade == "pass":
        return "🟢"
    if grade == "fail":
        return "🔴"
    return "⚪"


def get_trace_grade(trace_id: str) -> dict:
    """Return {'grade': ..., 'comment': ...} for a trace, or empty strings."""
    df = st.session_state.grades_df
    row = df.filter(df["trace_id"] == trace_id)
    if row.height == 0:
        return {"grade": "", "comment": ""}
    return {
        "grade": row["grade"][0] or "",
        "comment": row["comment"][0] or "",
    }


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    init_state()
    traces = load_traces()
    n = len(traces)
    idx = st.session_state.current_index

    # Build a lookup of grades for the sidebar
    grade_lookup = {}
    for t in traces:
        info = get_trace_grade(t["trace_id"])
        grade_lookup[t["trace_id"]] = info["grade"]

    # ── Sidebar ──────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("📝 Trace Grader")
        st.divider()

        # Progress
        graded_count = sum(1 for g in grade_lookup.values() if g in ("pass", "fail"))
        st.metric("Progress", f"{graded_count} / {n}")
        st.progress(graded_count / n if n else 0)

        passed = sum(1 for g in grade_lookup.values() if g == "pass")
        failed = sum(1 for g in grade_lookup.values() if g == "fail")
        cols = st.columns(3)
        cols[0].metric("Pass", passed)
        cols[1].metric("Fail", failed)
        cols[2].metric("Todo", n - graded_count)

        st.divider()

        # Trace list
        st.subheader("Traces")
        for i, t in enumerate(traces):
            tid = t["trace_id"]
            icon = grade_color(grade_lookup.get(tid))
            label = f"{icon} {tid}"
            if st.button(label, key=f"nav_{tid}", use_container_width=True):
                st.session_state.current_index = i
                st.rerun()

        st.divider()

        # Prev / Next
        nav_cols = st.columns(2)
        with nav_cols[0]:
            if st.button("← Prev", use_container_width=True, disabled=idx == 0):
                st.session_state.current_index -= 1
                st.rerun()
        with nav_cols[1]:
            if st.button("Next →", use_container_width=True, disabled=idx >= n - 1):
                st.session_state.current_index += 1
                st.rerun()

    # ── Main area ────────────────────────────────────────────────────────
    trace = traces[idx]
    tid = trace["trace_id"]
    existing = get_trace_grade(tid)

    # Header
    header_cols = st.columns([3, 2, 2])
    with header_cols[0]:
        st.header(f"{tid}")
    with header_cols[1]:
        st.caption("Scenario")
        st.write(trace["scenario"])
    with header_cols[2]:
        meta = trace.get("metadata", {})
        st.caption("Metadata")
        discount_tag = "🏷️ Discount" if meta.get("has_discount") else "No discount"
        st.write(f"{discount_tag} · {meta.get('product_category', '')}")

    st.divider()

    # Chat display
    for turn in trace["turns"]:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

    st.divider()

    # ── Grading controls ─────────────────────────────────────────────────
    st.subheader("Grade this trace")

    # Grade buttons
    btn_cols = st.columns([1, 1, 4])
    grade_value = existing["grade"]

    with btn_cols[0]:
        pass_variant = "primary" if grade_value == "pass" else "secondary"
        if st.button("✅ Pass", use_container_width=True, type=pass_variant):
            grade_value = "pass"

    with btn_cols[1]:
        fail_variant = "primary" if grade_value == "fail" else "secondary"
        if st.button("❌ Fail", use_container_width=True, type=fail_variant):
            grade_value = "fail"

    # Comment
    comment = st.text_area(
        "Comment (optional)",
        value=existing["comment"],
        placeholder="Add notes about this trace…",
        key=f"comment_{tid}",
    )

    # Save
    save_cols = st.columns([1, 5])
    with save_cols[0]:
        if st.button("💾 Save", use_container_width=True, type="primary"):
            if not grade_value:
                st.warning("Please select Pass or Fail before saving.")
            else:
                st.session_state.grades_df = save_grade(
                    GRADES_PATH, tid, grade_value, comment
                )
                st.success(f"Saved **{grade_value.upper()}** for {tid}")
                st.rerun()

    # Current status indicator
    if existing["grade"]:
        st.info(
            f"Current grade: **{existing['grade'].upper()}**"
            + (f" — \"{existing['comment']}\"" if existing["comment"] else "")
        )


if __name__ == "__main__":
    main()
