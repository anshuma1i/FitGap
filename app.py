"""FitGap demo UI: paste a candidate, get ranked assignments with fit-gap.

One screen, intentionally:
  - sidebar: signal blend + top-N + sample-candidate picker
  - main:    candidate workspace, Match button, ranked result cards

Run with: streamlit run app.py
"""

from html import escape

import streamlit as st

from data import ASSIGNMENTS, CANDIDATES
from matcher import DEFAULT_ALPHA, MatchResult, extract_skills, rank_assignments


st.set_page_config(
    page_title="FitGap",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_theme() -> None:
    """Apply the FitGap visual system on top of Streamlit defaults."""
    st.markdown(
        """
        <style>
        :root {
            --fg-ink: #101820;
            --fg-muted: #5c6773;
            --fg-line: rgba(16, 24, 32, 0.12);
            --fg-panel: rgba(255, 255, 255, 0.88);
            --fg-accent: #0ea5a3;
            --fg-cyan: #1aa7c8;
            --fg-green: #1e8a66;
            --fg-red: #b74747;
            --fg-amber: #b97919;
            --fg-graphite: #17212b;
        }

        .stApp {
            background:
                linear-gradient(135deg, rgba(14, 165, 163, 0.10), transparent 28rem),
                linear-gradient(180deg, #f7faf9 0%, #edf1f3 100%);
            color: var(--fg-ink);
        }

        /* Keep the header element so the sidebar collapse toggle stays
           accessible, but make it visually invisible. */
        [data-testid="stHeader"] {
            background: transparent;
            box-shadow: none;
        }

        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {
            display: none;
        }

        [data-testid="stSidebar"] {
            background: var(--fg-graphite);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebarContent"] {
            padding-left: 1.35rem;
            padding-right: 1.35rem;
        }

        [data-testid="stSidebar"] * {
            color: #edf5f4;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label p {
            color: rgba(237, 245, 244, 0.82);
        }

        [data-testid="stSidebar"] [data-baseweb="select"] * {
            color: var(--fg-ink);
        }

        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 8px;
        }

        /* Slider readability on the dark sidebar -- targets BaseWeb internals
           that Streamlit doesn't theme for us. */
        [data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
            background: var(--fg-accent);
            border: 2px solid #ffffff;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
        }
        [data-testid="stSidebar"] [data-baseweb="slider"] > div > div {
            background: rgba(255, 255, 255, 0.20);
        }
        [data-testid="stSidebar"] [data-baseweb="slider"] > div > div > div {
            background: var(--fg-accent);
        }
        [data-testid="stSidebar"] [data-testid="stTickBar"] {
            color: rgba(237, 245, 244, 0.60);
        }
        [data-testid="stSidebar"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
            color: #ffffff;
            font-weight: 700;
        }

        .block-container {
            max-width: 1220px;
            padding-top: 2.6rem;
            padding-bottom: 3rem;
        }

        .app-head {
            border-bottom: 1px solid var(--fg-line);
            margin-bottom: 1.25rem;
            padding-bottom: 1rem;
        }

        .brand-row {
            align-items: center;
            color: var(--fg-muted);
            display: flex;
            font-size: 0.78rem;
            font-weight: 700;
            gap: 0.55rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .brand-dot {
            background: linear-gradient(135deg, var(--fg-accent), var(--fg-amber));
            border-radius: 999px;
            display: inline-block;
            height: 0.62rem;
            width: 0.62rem;
        }

        .app-title {
            color: var(--fg-ink);
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            line-height: 1.05;
            margin: 0;
        }

        .app-subtitle {
            color: var(--fg-muted);
            font-size: 1rem;
            line-height: 1.5;
            margin: 0.55rem 0 0;
            max-width: 38rem;
        }

        .status-strip {
            align-items: stretch;
            display: grid;
            gap: 0.75rem;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            margin: 0 0 1rem;
        }

        .status-item {
            background: rgba(255, 255, 255, 0.66);
            border: 1px solid var(--fg-line);
            border-radius: 8px;
            padding: 0.72rem 0.85rem;
        }

        .status-item span {
            color: var(--fg-muted);
            display: block;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .status-item strong {
            color: var(--fg-ink);
            display: block;
            font-size: 1.12rem;
            line-height: 1.35;
            margin-top: 0.12rem;
        }

        .section-label {
            color: var(--fg-muted);
            font-size: 0.78rem;
            font-weight: 780;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
        }

        .subtle-note {
            color: var(--fg-muted);
            font-size: 0.88rem;
            margin-top: 0.55rem;
        }

        div[data-testid="stTextArea"] textarea {
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(16, 24, 32, 0.14);
            border-radius: 8px;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
            color: var(--fg-ink);
            font-size: 0.96rem;
            line-height: 1.5;
            min-height: 180px;
        }

        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--fg-accent);
            box-shadow: 0 0 0 3px rgba(14, 165, 163, 0.16);
        }

        .stButton > button {
            background: var(--fg-graphite);
            border: 1px solid rgba(16, 24, 32, 0.12);
            border-radius: 8px;
            box-shadow: 0 10px 24px rgba(23, 33, 43, 0.15);
            color: #ffffff;
            font-weight: 760;
            letter-spacing: 0;
            min-height: 2.85rem;
        }

        .stButton > button:hover,
        .stButton > button:focus {
            background: #0f171f;
            border-color: var(--fg-accent);
            color: #ffffff;
        }

        .skill-panel {
            background: rgba(255, 255, 255, 0.58);
            border: 1px solid var(--fg-line);
            border-radius: 8px;
            padding: 1rem;
        }

        .skill-count {
            color: var(--fg-ink);
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 1.72rem;
            font-weight: 800;
            line-height: 1;
            margin: 0.1rem 0 0.75rem;
        }

        .results-head {
            align-items: end;
            border-top: 1px solid var(--fg-line);
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            margin-top: 1.25rem;
            padding-top: 1.15rem;
        }

        .results-head h2 {
            color: var(--fg-ink);
            font-size: 1.28rem;
            letter-spacing: 0;
            line-height: 1.25;
            margin: 0;
        }

        .run-meta {
            color: var(--fg-muted);
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.82rem;
            text-align: right;
        }

        .result-card {
            background: var(--fg-panel);
            border: 1px solid rgba(16, 24, 32, 0.11);
            border-radius: 8px;
            box-shadow: 0 16px 34px rgba(23, 33, 43, 0.08);
            margin-top: 0.9rem;
            overflow: hidden;
        }

        .result-topline {
            background: linear-gradient(90deg, var(--fg-accent), var(--fg-cyan), var(--fg-amber));
            height: 3px;
        }

        .result-topline.is-review {
            background: var(--fg-red);
        }

        .result-card.is-review {
            border-color: rgba(183, 71, 71, 0.32);
            box-shadow: 0 16px 34px rgba(183, 71, 71, 0.12);
        }

        .result-body {
            padding: 1.05rem 1.1rem 1.1rem;
        }

        .result-header {
            align-items: start;
            display: grid;
            gap: 1rem;
            grid-template-columns: minmax(0, 1fr) auto;
        }

        .result-kicker {
            color: var(--fg-muted);
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .result-title {
            color: var(--fg-ink);
            font-size: 1.12rem;
            font-weight: 780;
            letter-spacing: 0;
            line-height: 1.25;
            margin-top: 0.15rem;
        }

        .status-badge {
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            padding: 0.35rem 0.62rem;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .status-review {
            background: rgba(183, 71, 71, 0.10);
            border: 1px solid rgba(183, 71, 71, 0.24);
            color: var(--fg-red);
        }

        .status-ready {
            background: rgba(30, 138, 102, 0.10);
            border: 1px solid rgba(30, 138, 102, 0.24);
            color: var(--fg-green);
        }

        .description {
            color: #29343d;
            font-size: 0.94rem;
            line-height: 1.5;
            margin: 0.85rem 0 1rem;
        }

        .score-grid {
            border-bottom: 1px solid var(--fg-line);
            border-top: 1px solid var(--fg-line);
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            margin: 0.85rem 0 1rem;
        }

        .score-cell {
            border-right: 1px solid var(--fg-line);
            padding: 0.72rem 0.8rem;
        }

        .score-cell:last-child {
            border-right: 0;
        }

        .score-cell span {
            color: var(--fg-muted);
            display: block;
            font-size: 0.72rem;
            font-weight: 760;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .score-cell strong {
            color: var(--fg-ink);
            display: block;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 1.18rem;
            margin: 0.22rem 0 0.35rem;
        }

        .meter {
            background: rgba(16, 24, 32, 0.08);
            border-radius: 999px;
            height: 0.32rem;
            overflow: hidden;
        }

        .meter span {
            border-radius: 999px;
            display: block;
            height: 100%;
        }

        .skill-row {
            align-items: start;
            display: grid;
            gap: 0.7rem;
            grid-template-columns: 9.5rem minmax(0, 1fr);
            margin-top: 0.62rem;
        }

        .skill-row-label {
            color: var(--fg-muted);
            font-size: 0.75rem;
            font-weight: 780;
            letter-spacing: 0.06em;
            padding-top: 0.18rem;
            text-transform: uppercase;
        }

        .chip-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }

        .chip {
            border-radius: 7px;
            font-size: 0.78rem;
            font-weight: 720;
            line-height: 1;
            padding: 0.42rem 0.52rem;
        }

        .chip-ok {
            background: rgba(30, 138, 102, 0.11);
            border: 1px solid rgba(30, 138, 102, 0.22);
            color: var(--fg-green);
        }

        .chip-missing {
            background: rgba(183, 71, 71, 0.10);
            border: 1px solid rgba(183, 71, 71, 0.22);
            color: var(--fg-red);
        }

        .chip-nice {
            background: rgba(26, 167, 200, 0.11);
            border: 1px solid rgba(26, 167, 200, 0.22);
            color: #126f86;
        }

        .chip-empty {
            background: rgba(16, 24, 32, 0.06);
            border: 1px solid rgba(16, 24, 32, 0.10);
            color: var(--fg-muted);
        }

        .review-callout {
            align-items: center;
            background: rgba(183, 71, 71, 0.09);
            border: 1px solid rgba(183, 71, 71, 0.24);
            border-left: 3px solid var(--fg-red);
            border-radius: 6px;
            color: var(--fg-red);
            display: flex;
            font-size: 0.86rem;
            font-weight: 720;
            gap: 0.55rem;
            margin-top: 0.95rem;
            padding: 0.65rem 0.85rem;
        }

        .review-callout::before {
            background: var(--fg-red);
            border-radius: 999px;
            content: "";
            display: inline-block;
            flex-shrink: 0;
            height: 0.5rem;
            width: 0.5rem;
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
        }

        .sidebar-toggle-btn {
            position: fixed;
            top: 0.85rem;
            left: 0.85rem;
            z-index: 999;
            background: var(--fg-graphite);
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 8px;
            color: #edf5f4;
            cursor: pointer;
            font-size: 1.1rem;
            height: 2.25rem;
            width: 2.25rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.15s, border-color 0.15s;
        }
        .sidebar-toggle-btn:hover {
            background: #0f171f;
            border-color: var(--fg-accent);
            color: #ffffff;
        }

        @media (max-width: 820px) {
            .status-strip,
            .score-grid,
            .result-header,
            .skill-row {
                grid-template-columns: 1fr;
            }

            .results-head {
                align-items: start;
                flex-direction: column;
            }

            .run-meta {
                text-align: left;
            }

            .score-cell {
                border-bottom: 1px solid var(--fg-line);
                border-right: 0;
            }

            .score-cell:last-child {
                border-bottom: 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _chips(skills: list[str], kind: str) -> str:
    """Render a row of skill chips as a single HTML string."""
    if not skills:
        return '<span class="chip chip-empty">none</span>'
    return " ".join(
        f'<span class="chip chip-{kind}">{escape(skill)}</span>'
        for skill in skills
    )


def _skill_row(label: str, skills: list[str], kind: str) -> str:
    return (
        '<div class="skill-row">'
        f'<div class="skill-row-label">{escape(label)}</div>'
        f'<div class="chip-list">{_chips(skills, kind)}</div>'
        "</div>"
    )


def _score_cell(label: str, value: float, color: str) -> str:
    pct = max(0, min(100, round(value * 100)))
    return (
        '<div class="score-cell">'
        f"<span>{escape(label)}</span>"
        f"<strong>{value:.2f}</strong>"
        '<div class="meter">'
        f'<span style="width:{pct}%; background:{color};"></span>'
        "</div>"
        "</div>"
    )


def _render_card(rank: int, r: MatchResult) -> None:
    a = r.assignment
    flagged = r.review_flag
    status_class = "status-review" if flagged else "status-ready"
    status_label = "Review" if flagged else "Ready"
    card_class = "result-card is-review" if flagged else "result-card"
    topline_class = "result-topline is-review" if flagged else "result-topline"

    skill_rows = [
        _skill_row("Matched", r.matched_required, "ok"),
        _skill_row("Missing", r.missing_required, "missing"),
    ]
    if a["nice_to_have"]:
        skill_rows.append(_skill_row("Nice to have", r.matched_nice, "nice"))

    scores = "".join(
        [
            _score_cell("Combined", r.combined_score, "var(--fg-accent)"),
            _score_cell("Semantic", r.semantic_sim, "var(--fg-cyan)"),
            _score_cell("Skill overlap", r.skill_overlap, "var(--fg-green)"),
            _score_cell("Confidence", r.confidence, "var(--fg-amber)"),
        ]
    )

    callout = ""
    if flagged:
        reason_text = "; ".join(r.review_reasons) or "Flagged for review"
        callout = f'<div class="review-callout">{escape(reason_text)}</div>'

    # Build the card as a single concatenated string. A multi-line f-string
    # with an empty placeholder (e.g. callout="") leaves a whitespace-only
    # line, which markdown treats as the end of the HTML block; everything
    # after it then renders as code. Flat string avoids the trap.
    html = (
        f'<article class="{card_class}">'
        f'<div class="{topline_class}"></div>'
        '<div class="result-body">'
        '<div class="result-header">'
        '<div>'
        f'<div class="result-kicker">#{rank:02d} / {escape(a["id"])}</div>'
        f'<div class="result-title">{escape(a["title"])}</div>'
        '</div>'
        f'<div class="status-badge {status_class}">{status_label}</div>'
        '</div>'
        f'<p class="description">{escape(a["description"])}</p>'
        f'<div class="score-grid">{scores}</div>'
        f'{"".join(skill_rows)}'
        f'{callout}'
        '</div>'
        '</article>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _render_results_header(result_count: int, alpha: float) -> None:
    st.markdown(
        f"""
        <div class="results-head">
            <div>
                <div class="section-label">Ranked assignments</div>
                <h2>Top {result_count} matches</h2>
            </div>
            <div class="run-meta">alpha={alpha:.2f} / assignments={len(ASSIGNMENTS)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_inject_theme()

# Floating button that programmatically clicks Streamlit's hidden
# sidebar-toggle button so users can always open/close the sidebar.
st.markdown(
    """
    <button class="sidebar-toggle-btn" onclick="
      (function(){
        var btn = window.parent.document.querySelector(
          '[data-testid=\"stSidebar\"] button[data-testid=\"baseButton-header\"]'
        );
        if(btn) btn.click();
      })();
    " title="Toggle sidebar">☰</button>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="app-head">'
    '<h1 class="app-title">FitGap</h1>'
    '<p class="app-subtitle">Recruiter-facing assignment matcher with '
    'confidence and a REVIEW flag for matches worth a second look.</p>'
    "</div>",
    unsafe_allow_html=True,
)


# ---- Sidebar: tunables ----------------------------------------------------

with st.sidebar:
    st.header("Controls")
    alpha = st.slider(
        "Semantic weight",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_ALPHA,
        step=0.05,
        help=(
            "Combined score = semantic weight * semantic similarity + "
            "(1 - semantic weight) * required-skill overlap."
        ),
    )
    top_n = st.slider("Visible matches", 3, len(ASSIGNMENTS), 5)

    st.divider()
    st.header("Candidate")
    sample_idx = st.selectbox(
        "Preset",
        options=list(range(len(CANDIDATES))),
        format_func=lambda i: CANDIDATES[i]["name"],
        index=0,
    )


# ---- Input ----------------------------------------------------------------

# Keep the textarea in sync with the sidebar sample picker without trashing
# whatever the user has typed manually.
if "candidate_text" not in st.session_state:
    st.session_state.candidate_text = CANDIDATES[0]["blurb"]
if st.session_state.get("loaded_sample") != sample_idx:
    st.session_state.candidate_text = CANDIDATES[sample_idx]["blurb"]
    st.session_state.loaded_sample = sample_idx
    st.session_state.has_rendered_results = False

st.markdown(
    f"""
    <div class="status-strip">
        <div class="status-item">
            <span>Open assignments</span>
            <strong>{len(ASSIGNMENTS)}</strong>
        </div>
        <div class="status-item">
            <span>Candidate presets</span>
            <strong>{len(CANDIDATES)}</strong>
        </div>
        <div class="status-item">
            <span>Visible matches</span>
            <strong>{top_n}</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

input_col, skill_col = st.columns([3, 1], gap="large")
with input_col:
    st.markdown(
        '<div class="section-label">Candidate signal</div>',
        unsafe_allow_html=True,
    )
    candidate_text = st.text_area(
        "Candidate signal",
        key="candidate_text",
        height=190,
        label_visibility="collapsed",
    )
    extracted_live = sorted(extract_skills(candidate_text))

    action_col, note_col = st.columns([1, 3], vertical_alignment="center")
    with action_col:
        run = st.button("Run Match", type="primary", use_container_width=True)
    with note_col:
        words = len(candidate_text.split())
        st.markdown(
            f'<div class="subtle-note">{words} words / '
            f'{len(extracted_live)} skills detected</div>',
            unsafe_allow_html=True,
        )

with skill_col:
    preview_skills = extracted_live[:12]
    extra_count = max(len(extracted_live) - len(preview_skills), 0)
    skill_preview = "".join(
        f'<span class="chip chip-nice">{escape(skill)}</span>'
        for skill in preview_skills
    )
    if extra_count:
        skill_preview += f'<span class="chip chip-empty">+{extra_count}</span>'
    if not skill_preview:
        skill_preview = '<span class="chip chip-empty">none detected</span>'
    st.markdown(
        f"""
        <div class="skill-panel">
            <div class="section-label">Detected skills</div>
            <div class="skill-count">{len(extracted_live)}</div>
            <div class="chip-list">{skill_preview}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---- Run + render ---------------------------------------------------------

should_show_results = bool(candidate_text.strip()) and (
    run or not st.session_state.get("has_rendered_results")
)
if run:
    st.session_state.has_rendered_results = True

if should_show_results:
    st.session_state.has_rendered_results = True
    with st.spinner("Embedding and scoring..."):
        results = rank_assignments(candidate_text, ASSIGNMENTS, alpha=alpha)

    visible_results = results[:top_n]
    _render_results_header(len(visible_results), alpha)
    for i, r in enumerate(visible_results, start=1):
        _render_card(i, r)
elif run:
    st.info("Paste a candidate blurb to match.")
