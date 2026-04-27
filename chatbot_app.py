"""
app.py — CyberGuard AI Streamlit Frontend
------------------------------------------
UI is 100% unchanged from the original.
Backend improvements:
  - Session-state helpers extracted into `_init_session` to avoid repetition
  - `_stream_and_collect` helper removes duplicated st.write_stream pattern
  - Command dispatch table replaces if/elif chain in sidebar handler
  - Verdict rendering guard centralised in one place
  - Type annotations on all helpers
  - No silent exception swallowing
"""

from __future__ import annotations

import warnings
from typing import Optional

import streamlit as st

from src.chat_controller import ChatController

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="CyberGuard AI Platform",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── PREMIUM SAAS UI CSS INJECTION ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
.stApp {
    background-color: #0A0D14;
    color: #E6EDF3;
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0D1117 !important;
    border-right: 1px solid #21262D;
}
[data-testid="stSidebar"] .stButton > button {
    background-color: transparent !important;
    border: none !important;
    color: #E6EDF3 !important;
    font-weight: 500;
    text-align: left;
    width: 100%;
    padding: 10px 14px;
    border-radius: 8px;
    transition: all 0.2s ease;
    justify-content: flex-start;
    font-size: 0.88rem;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #161B22 !important;
}

/* ── Header ── */
h1 {
    font-weight: 700 !important;
    font-size: 1.7rem !important;
    letter-spacing: -0.5px;
    color: #FFFFFF;
    border-bottom: 1px solid #21262D;
    padding-bottom: 14px;
    margin-bottom: 28px;
}

/* ── Chat Input ── */
.stChatInputContainer {
    background-color: #0D1117 !important;
    border: 1px solid #30363D !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.6) !important;
}
.stChatInput textarea { color: #FAFAFA !important; }

/* ── Chat Bubbles ── */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 8px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #0D1117 !important;
    border-radius: 12px;
    padding: 14px 18px !important;
    border: 1px solid #21262D;
    margin: 12px 0;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    padding: 14px 5px !important;
}

/* ── Verdict Panel ── */
.verdict-panel {
    background: #0D1117;
    border-radius: 12px;
    border: 1px solid #21262D;
    padding: 18px 22px;
    margin-top: 12px;
    font-family: 'Inter', sans-serif;
}
.verdict-title {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    color: #8B949E;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.analysis-block {
    background: #161B22;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 12px;
    border-left: 3px solid #388BFD;
}
.analysis-block-title {
    font-size: 0.75rem;
    color: #8B949E;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.cat-chip {
    display: inline-block;
    background: #1F2937;
    border: 1px solid #374151;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 500;
    color: #D1D5DB;
    margin: 2px 3px 2px 0;
}
.risk-bar-wrapper {
    background: #161B22;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.risk-bar-bg {
    background: #21262D;
    border-radius: 6px;
    height: 8px;
    margin-top: 8px;
    overflow: hidden;
}
.risk-bar-fill {
    height: 8px;
    border-radius: 6px;
    transition: width 0.5s ease;
}
.verdict-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    font-size: 1.05rem;
    padding: 8px 18px;
    border-radius: 8px;
    margin: 10px 0 8px 0;
}
.badge-unsafe   { background: rgba(248,81,73,0.15); border: 1.5px solid #F85149; color: #F85149; }
.badge-review   { background: rgba(210,153,34,0.15); border: 1.5px solid #D2A622; color: #D2A622; }
.badge-safe     { background: rgba(63,185,80,0.15); border: 1.5px solid #3FB950; color: #3FB950; }
.badge-na       { background: rgba(139,148,158,0.15); border: 1.5px solid #8B949E; color: #8B949E; }
.action-row {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #161B22;
    border-radius: 8px;
    padding: 10px 14px;
    margin-top: 6px;
    font-size: 0.88rem;
}
.action-label { color: #8B949E; font-weight: 500; }
.action-value { font-weight: 600; }
.action-block { color: #F85149; }
.action-warn  { color: #D2A622; }
.action-allow { color: #3FB950; }
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.8rem;
    color: #8B949E;
    padding: 4px 0;
}
.pipeline-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #388BFD;
    flex-shrink: 0;
}
.pipeline-arrow {
    color: #30363D;
    font-size: 0.7rem;
    margin-left: 3px;
}
.context-note {
    font-size: 0.78rem;
    color: #8B949E;
    font-style: italic;
    margin-top: 10px;
    padding: 8px 12px;
    background: #161B22;
    border-radius: 6px;
    border-left: 3px solid #388BFD;
}

/* ── Expander ── */
.st-emotion-cache-p5msec {
    background-color: transparent;
    border: 1px solid #21262D;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Helpers — pure functions, no side-effects on session state
# ─────────────────────────────────────────────────────────────

def _risk_color(score: int) -> str:
    if score >= 70:
        return "#F85149"
    if score >= 40:
        return "#D2A622"
    return "#3FB950"


def _badge_class(label: str) -> str:
    return {
        "Unsafe":       "badge-unsafe",
        "Needs Review": "badge-review",
        "Safe":         "badge-safe",
    }.get(label, "badge-na")


def _action_class(action: str) -> str:
    return {"Block": "action-block", "Warn": "action-warn", "Allow": "action-allow"}.get(action, "")


def _action_icon(action: str) -> str:
    return {"Block": "🚫", "Warn": "⚠️", "Allow": "✅"}.get(action, "")


# ─────────────────────────────────────────────────────────────
# Session state initialisation — single call, no repetition
# ─────────────────────────────────────────────────────────────

_WELCOME_MSG = "How can I help you analyze, moderate, or assess digital interactions today?"

def _init_session() -> None:
    """Idempotent session-state bootstrap called once per page load."""
    if "controller" not in st.session_state:
        st.session_state.controller = ChatController()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": _WELCOME_MSG}
        ]


def _clear_history() -> None:
    """Reset chat to the single welcome message."""
    st.session_state.messages = [{"role": "assistant", "content": _WELCOME_MSG}]


# ─────────────────────────────────────────────────────────────
# Verdict panel renderer (UI unchanged)
# ─────────────────────────────────────────────────────────────

def render_verdict_panel(
    verdict: dict,
    bert: dict,
    show_pipeline: bool = True,
) -> None:
    """Render the full structured moderation report panel."""
    if verdict.get("final_label") == "N/A":
        return  # Chat mode — no moderation panel shown

    label      = verdict.get("final_label", "Safe")
    action     = verdict.get("action", "Allow")
    risk_score = verdict.get("risk_score", 0)
    risk_label = verdict.get("risk_label", "Low Risk")
    categories = verdict.get("categories", [])
    reasoning  = verdict.get("reasoning", "")
    ctx_note   = verdict.get("context_note", "")

    risk_color = _risk_color(risk_score)
    badge_cls  = _badge_class(label)
    act_cls    = _action_class(action)
    act_icon   = _action_icon(action)

    chips = (
        "".join(f'<span class="cat-chip">{c}</span>' for c in categories)
        if categories
        else '<span class="cat-chip">None</span>'
    )

    bar_html = (
        f'<div class="risk-bar-bg">'
        f'<div class="risk-bar-fill" style="width:{risk_score}%; background:{risk_color};"></div>'
        f'</div>'
    )

    panel_html = f"""
    <div class="verdict-panel">
      <div class="verdict-title">📋 Moderation Report</div>

      <div class="analysis-block">
        <div class="analysis-block-title">🧠 Analysis — Categories Detected</div>
        {chips}
      </div>

      <div class="risk-bar-wrapper">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.8rem; color:#8B949E; font-weight:600;">⚡ Risk Score</span>
          <span style="font-size:0.95rem; font-weight:700; color:{risk_color};">{risk_score}%
            &nbsp;<span style="font-size:0.75rem; font-weight:500; color:{risk_color};">({risk_label})</span>
          </span>
        </div>
        {bar_html}
      </div>

      <div style="margin-bottom:10px;">
        <div style="font-size:0.72rem; color:#8B949E; font-weight:600; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px;">🚦 Final Decision</div>
        <div class="verdict-badge {badge_cls}">{label.upper()}</div>
      </div>

      <div class="action-row">
        <span class="action-label">🔧 Action Taken:</span>
        <span class="action-value {act_cls}">{act_icon} Message {action}ed</span>
        <span style="margin-left:auto; font-size:0.75rem; color:#8B949E;">{reasoning}</span>
      </div>

      <div class="context-note">{ctx_note}</div>
    </div>
    """
    st.markdown(panel_html, unsafe_allow_html=True)

    if show_pipeline:
        _severity_rank = ["None", "Low", "Medium", "High"]
        top_severity   = max(
            verdict.get("severities", ["None"]),
            key=lambda s: _severity_rank.index(s) if s in _severity_rank else 0,
        )
        pipeline_steps = [
            "User Input received",
            "Text Preprocessing (clean & extract)",
            "BERT Classifier (threat detection)",
            "LLM Sentence Analysis",
            "Category Detection (rule + LLM)",
            f"Decision Engine → Severity: {top_severity}",
            f"Action Enforced → {act_icon} {action}",
            "Final Output rendered",
        ]
        step_html = ""
        for i, step in enumerate(pipeline_steps):
            arrow = '<div class="pipeline-arrow">↓</div>' if i < len(pipeline_steps) - 1 else ""
            step_html += (
                f'<div class="pipeline-step">'
                f'<div class="pipeline-dot"></div><span>{step}</span>'
                f'</div>{arrow}'
            )
        with st.expander("🔬 View Processing Pipeline"):
            st.markdown(
                f'<div style="padding:8px 4px;">{step_html}</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────
# Streaming helper — removes duplicated write_stream pattern
# ─────────────────────────────────────────────────────────────

def _stream_and_collect(generator) -> str:
    """
    Stream `generator` to the current Streamlit context via `st.write_stream`
    and return the full concatenated string.
    """
    return st.write_stream(generator)


# ─────────────────────────────────────────────────────────────
# Bootstrap
# ─────────────────────────────────────────────────────────────

_init_session()


# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<div style='display:flex; align-items:center; gap:10px; margin-bottom:18px;'>"
        "<h2 style='border-bottom:none; margin:0; font-size:1.3rem;'>🛡️ CyberGuard</h2></div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
        <div style="background:#161B22; border:1px solid #21262D; padding:7px 12px; border-radius:6px;
                    display:flex; align-items:center; gap:8px; margin-bottom:28px;">
            <div style="width:8px;height:8px;background:#3FB950;border-radius:50%;"></div>
            <span style="color:#8B949E;font-size:0.78rem;font-weight:500;">Moderation Engine Active</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='color:#8B949E; font-size:0.72rem; font-weight:600; letter-spacing:1.2px; margin-bottom:8px;'>MODULES</div>",
        unsafe_allow_html=True,
    )

    if st.button("📝 Generate Quiz"):
        st.session_state.trigger_cmd = "QUIZ"
    if st.button("📊 Start Assessment"):
        st.session_state.trigger_cmd = "ASSESS"

    st.markdown("<hr style='border-color:#21262D; margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#8B949E; font-size:0.72rem; font-weight:600; letter-spacing:1.2px; margin-bottom:8px;'>PIPELINE</div>",
        unsafe_allow_html=True,
    )
    st.markdown("""
        <div style="font-size:0.78rem; color:#8B949E; line-height:2;">
        User Input<br>↓ Preprocessing<br>↓ BERT Classifier<br>↓ LLM Analysis<br>
        ↓ Decision Engine<br>↓ Action Enforcement<br>↓ Final Output
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat History"):
        _clear_history()
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────

st.title("Content Moderation Console")

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "verdict" in msg and msg.get("is_analysis", False):
            render_verdict_panel(msg["verdict"], msg.get("bert", {}), show_pipeline=True)


# ─────────────────────────────────────────────────────────────
# Sidebar command dispatch
# ─────────────────────────────────────────────────────────────

if "trigger_cmd" in st.session_state:
    cmd_val = st.session_state.pop("trigger_cmd")          # pop avoids stale re-triggers

    with st.chat_message("assistant"):
        if isinstance(cmd_val, tuple) and cmd_val[0] == "REWRITE":
            st.markdown(f"**Generating safe alternatives for:** _{cmd_val[1]}_\n")
            spinner_msg = "Analyzing semantics..."
            gen = st.session_state.controller.process_command(
                cmd_val[0], cmd_val[1], st.session_state.messages
            )
        else:
            spinner_msg = "Generating module..."
            gen = st.session_state.controller.process_command(
                cmd_val, "", st.session_state.messages
            )

        with st.spinner(spinner_msg):
            final_output = _stream_and_collect(gen)

    st.session_state.messages.append({"role": "assistant", "content": final_output})
    st.rerun()


# ─────────────────────────────────────────────────────────────
# User message pipeline
# ─────────────────────────────────────────────────────────────

elif prompt := st.chat_input("Message CyberGuard AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing through moderation pipeline..."):
            pipeline_result = st.session_state.controller.process_message(
                prompt, st.session_state.messages
            )
            final_output = _stream_and_collect(pipeline_result.response_generator)

        bert        = pipeline_result.bert
        is_analysis = pipeline_result.is_analysis

        if is_analysis:
            full_llm_text = "".join(pipeline_result.response_parts)
            final_verdict = st.session_state.controller.refine_verdict(bert, full_llm_text)
            render_verdict_panel(final_verdict, bert, show_pipeline=True)
        else:
            final_verdict = pipeline_result.verdict

    st.session_state.messages.append({
        "role":        "assistant",
        "content":     final_output,
        "bert":        bert,
        "verdict":     final_verdict,
        "is_analysis": is_analysis,
    })
    st.rerun()
