"""
AI-Powered Legal Contract Analyzer
Main Streamlit Application
"""

import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

# ─── Page Config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="LexAI — Legal Contract Analyzer",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design System CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

/* ── CSS Variables ── */
:root {
    --navy:       #0F1B35;
    --slate:      #1E3A5F;
    --steel:      #2D5A8E;
    --accent:     #2D7DD2;
    --accent-lt:  #60A5FA;
    --teal:       #0D9488;

    --crit:       #DC2626;
    --crit-bg:    #FEF2F2;
    --crit-bdr:   #FECACA;
    --high:       #EA580C;
    --high-bg:    #FFF7ED;
    --high-bdr:   #FED7AA;
    --med:        #D97706;
    --med-bg:     #FFFBEB;
    --med-bdr:    #FDE68A;
    --low:        #16A34A;
    --low-bg:     #F0FDF4;
    --low-bdr:    #BBF7D0;

    --bg:         #F8FAFC;
    --surface:    #FFFFFF;
    --surface2:   #F1F5F9;
    --border:     #E2E8F0;
    --text:       #0F172A;
    --text-2:     #475569;
    --text-3:     #94A3B8;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
    color: var(--text);
}
.stApp { background: var(--bg); }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem; max-width: 1400px; }

/* ── App Header Banner ── */
.app-header {
    background: linear-gradient(135deg, var(--navy) 0%, var(--slate) 60%, var(--steel) 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    box-shadow: 0 4px 24px rgba(15,27,53,0.18);
}
.app-header-icon { font-size: 3rem; line-height: 1; }
.app-header h1 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    font-weight: 400;
    color: #F8FAFC;
    margin: 0;
    letter-spacing: -0.01em;
}
.app-header p {
    color: #94A3B8;
    font-size: 0.875rem;
    margin: 0.25rem 0 0;
    font-weight: 400;
}
.app-header .badge {
    background: rgba(45,125,210,0.25);
    color: var(--accent-lt);
    border: 1px solid rgba(96,165,250,0.3);
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 0.2rem 0.65rem;
    display: inline-block;
    margin-top: 0.4rem;
    text-transform: uppercase;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--navy);
    border-right: 1px solid rgba(255,255,255,0.07);
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #94A3B8;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] span {
    color: #CBD5E1 !important;
    font-size: 0.875rem;
}

/* ── Metric Cards ── */
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1rem 0; }
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.metric-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.35rem;
}
.metric-card .label {
    font-size: 0.75rem;
    color: var(--text-2);
    font-weight: 500;
    letter-spacing: 0.03em;
}
.metric-card.crit .value { color: var(--crit); }
.metric-card.high .value { color: var(--high); }
.metric-card.med  .value { color: var(--med); }
.metric-card.low  .value { color: var(--low); }

/* ── Risk Score Bar ── */
.score-bar-wrap { background: var(--surface2); border-radius: 999px; height: 8px; overflow: hidden; margin: 0.5rem 0; }
.score-bar { height: 100%; border-radius: 999px; transition: width 0.6s ease; }

/* ── Clause Cards ── */
.clause-card {
    background: var(--surface);
    border-radius: 12px;
    border-left: 4px solid var(--border);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s, transform 0.15s;
}
.clause-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.08); transform: translateY(-1px); }
.clause-card.risk-Critical { border-left-color: var(--crit); background: var(--crit-bg); }
.clause-card.risk-High     { border-left-color: var(--high); background: var(--high-bg); }
.clause-card.risk-Medium   { border-left-color: var(--med);  background: var(--med-bg);  }
.clause-card.risk-Low      { border-left-color: var(--low);  background: var(--low-bg);  }

.clause-header { display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.clause-index {
    background: var(--navy);
    color: white;
    border-radius: 6px;
    padding: 0.2rem 0.55rem;
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 2px;
}
.clause-heading { font-weight: 600; font-size: 0.95rem; color: var(--text); flex: 1; }
.clause-type-badge {
    font-size: 0.7rem;
    font-weight: 600;
    background: rgba(45,125,210,0.12);
    color: var(--accent);
    border: 1px solid rgba(45,125,210,0.2);
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    white-space: nowrap;
}
.risk-badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    white-space: nowrap;
    letter-spacing: 0.03em;
}
.risk-badge.Critical { background: var(--crit-bg); color: var(--crit); border: 1px solid var(--crit-bdr); }
.risk-badge.High     { background: var(--high-bg); color: var(--high); border: 1px solid var(--high-bdr); }
.risk-badge.Medium   { background: var(--med-bg);  color: var(--med);  border: 1px solid var(--med-bdr);  }
.risk-badge.Low      { background: var(--low-bg);  color: var(--low);  border: 1px solid var(--low-bdr);  }

.clause-explanation {
    font-size: 0.85rem;
    color: #1E293B !important;
    line-height: 1.6;
    margin: 0.5rem 0;
    padding: 0.75rem;
    background: rgba(255,255,255,0.88);
    border-radius: 8px;
}
.review-points { margin-top: 0.75rem; }
.review-point {
    font-size: 0.8rem;
    color: #334155 !important;
    padding: 0.3rem 0;
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
    border-top: 1px solid rgba(0,0,0,0.08);
}
.review-point::before { content: "▸"; color: var(--accent); font-size: 0.75rem; margin-top: 1px; flex-shrink: 0; }
/* Force dark text in all clause cards */
.clause-card .clause-explanation { color: #1E293B !important; }
.clause-card .review-point { color: #334155 !important; }
.clause-card .clause-heading { color: #0F172A !important; }
.clause-card p, .clause-card span, .clause-card div { color: inherit; }

/* ── Summary Card ── */
.summary-card {
    background: linear-gradient(135deg, var(--navy), var(--slate));
    border-radius: 14px;
    padding: 1.75rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
}
.summary-card h2 { font-family: 'DM Serif Display', serif; font-weight: 400; color: white; margin: 0 0 0.5rem; font-size: 1.5rem; }
.summary-card .meta { color: #94A3B8; font-size: 0.85rem; margin-bottom: 1.25rem; }
.summary-findings { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 1rem; }
.finding-item {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #CBD5E1;
    line-height: 1.5;
}
.finding-item::before { content: "→ "; color: var(--accent-lt); font-weight: 600; }

/* ── Q&A Section ── */
.qa-bubble {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    font-size: 0.875rem;
    line-height: 1.65;
    color: var(--text);
}
.qa-bubble.user {
    background: rgba(45,125,210,0.06);
    border-color: rgba(45,125,210,0.2);
    border-radius: 12px 12px 4px 12px;
}
.qa-bubble.assistant {
    border-radius: 4px 12px 12px 12px;
}
.qa-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.4rem; }
.qa-label.user { color: var(--accent); }
.qa-label.assistant { color: var(--teal); }

/* ── Section Headers ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--navy);
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Disclaimer ── */
.disclaimer-bar {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.78rem;
    color: #92400E;
    margin: 1rem 0;
    line-height: 1.5;
}

/* ── Upload Area ── */
.upload-hint {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 2.5rem;
    text-align: center;
    color: var(--text-3);
    font-size: 0.9rem;
}
.upload-hint .icon { font-size: 3rem; margin-bottom: 0.75rem; }
.upload-hint strong { color: var(--text-2); display: block; margin-bottom: 0.25rem; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--steel));
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.55rem 1.25rem;
    font-size: 0.875rem;
    transition: opacity 0.2s, transform 0.15s;
}
.stButton > button:hover { opacity: 0.9; transform: translateY(-1px); }

/* ── Progress ── */
.stProgress > div > div { background: linear-gradient(90deg, var(--accent), var(--teal)); border-radius: 999px; }

/* ── Selectbox, text input ── */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    border-radius: 8px !important;
    border-color: var(--border) !important;
    font-size: 0.875rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 0.25rem; border-bottom: 2px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    font-weight: 500;
    color: var(--text-2);
    padding: 0.6rem 1.2rem;
}
.stTabs [aria-selected="true"] { background: var(--surface); color: var(--accent) !important; border-bottom: 2px solid var(--accent); }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: var(--navy) !important;
}

/* ── Toast-like info box ── */
.info-box {
    background: rgba(45,125,210,0.07);
    border: 1px solid rgba(45,125,210,0.2);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    font-size: 0.83rem;
    color: var(--steel);
    line-height: 1.55;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────

RISK_COLORS_HEX = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#D97706",
    "Low": "#16A34A",
}

RISK_SCORE_BAR_COLORS = {
    "Critical": "linear-gradient(90deg, #DC2626, #EF4444)",
    "High": "linear-gradient(90deg, #EA580C, #F97316)",
    "Medium": "linear-gradient(90deg, #D97706, #FBBF24)",
    "Low": "linear-gradient(90deg, #16A34A, #22C55E)",
}


def score_bar_html(score: int, level: str) -> str:
    color = RISK_SCORE_BAR_COLORS.get(level, "#94A3B8")
    return f"""
    <div style="display:flex;align-items:center;gap:0.75rem;">
        <div class="score-bar-wrap" style="flex:1;">
            <div class="score-bar" style="width:{score}%;background:{color};"></div>
        </div>
        <span style="font-size:0.8rem;font-weight:700;color:{RISK_COLORS_HEX.get(level,'#64748B')};min-width:3rem;text-align:right;">{score}/100</span>
    </div>
    """


def render_clause_card(clause: dict):
    level = clause.get("risk_level", "Low")
    score = clause.get("risk_score", 0)
    heading = clause.get("heading", "Clause")[:100]
    ctype = clause.get("type", "General")
    explanation = clause.get("explanation", "")
    review_pts = clause.get("review_points", [])
    idx = clause.get("index", "")
    text = clause.get("text", "")

    review_html = "".join(
        f'<div class="review-point" style="color:#334155!important;">{pt}</div>'
        for pt in review_pts
    )

    bar = score_bar_html(score, level)

    st.html(f"""
    <div class="clause-card risk-{level}">
        <div class="clause-header">
            <span class="clause-index">#{idx}</span>
            <span class="clause-heading">{heading}</span>
            <span class="clause-type-badge">{ctype}</span>
            <span class="risk-badge {level}">{level}</span>
        </div>
        {bar}
        <div class="clause-explanation" style="color:#1E293B!important;font-size:0.85rem;">{explanation}</div>
        <div class="review-points">{review_html}</div>
    </div>
    """)

    with st.expander("📄 View original clause text"):
        st.text(text[:1200] + ("..." if len(text) > 1200 else ""))


def render_metric_grid(risk_counts: dict, avg_score: float):
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card crit">
            <div class="value">{risk_counts.get('Critical', 0)}</div>
            <div class="label">Critical Risks</div>
        </div>
        <div class="metric-card high">
            <div class="value">{risk_counts.get('High', 0)}</div>
            <div class="label">High Risks</div>
        </div>
        <div class="metric-card med">
            <div class="value">{risk_counts.get('Medium', 0)}</div>
            <div class="label">Medium Risks</div>
        </div>
        <div class="metric-card low" style="border-color:var(--low);">
            <div class="value" style="color:var(--accent);">{avg_score:.0f}</div>
            <div class="label">Avg Risk Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_gemini_client(api_key: str):
    from utils.gemini_client import get_gemini_client as _create_client
    return _create_client(api_key)


# ─── Main App ─────────────────────────────────────────────────────────────────

def main():
    # ── App Header ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="app-header">
        <div class="app-header-icon">⚖</div>
        <div>
            <h1>LexAI — Legal Contract Analyzer</h1>
            <p>AI-powered clause extraction, risk scoring, and contract intelligence using GenAI & RAG</p>
            <span class="badge">Powered by Google Gemini · RAG · Agentic Workflow</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-bar">
        ⚠️ <strong>Informational Use Only:</strong> This tool provides AI-assisted analysis for educational purposes.
        It does not constitute professional legal advice. Always consult a qualified attorney before making legal decisions.
    </div>
    """, unsafe_allow_html=True)

    # Load API Key from environment
    api_key = os.getenv("GEMINI_API_KEY", "")

    # ── Sidebar ─────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔧 Analysis Options")
        use_ai = st.toggle("Use AI Classification", value=True, help="Faster if disabled (heuristic mode)")
        filter_level = st.selectbox(
            "Filter by Risk Level",
            ["All", "Critical", "High", "Medium", "Low"],
        )
        sort_by = st.selectbox(
            "Sort Clauses By",
            ["Risk Score ↓", "Risk Score ↑", "Clause Index"],
        )

        st.markdown("---")
        st.markdown("### 📖 About")
        st.markdown("""
        <p style="color:#94A3B8;font-size:0.8rem;line-height:1.6;">
        Final-year GenAI project demonstrating:<br>
        • Clause extraction & classification<br>
        • Risk scoring (0–100)<br>
        • RAG-grounded explanations<br>
        • Agentic AI workflow<br>
        • Downloadable PDF reports
        </p>
        """, unsafe_allow_html=True)

    # ── Session State ────────────────────────────────────────────────────
    if "analyzed_clauses" not in st.session_state:
        st.session_state.analyzed_clauses = []
    if "contract_text" not in st.session_state:
        st.session_state.contract_text = ""
    if "summary" not in st.session_state:
        st.session_state.summary = {}
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    # ── Upload Section ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">📁 Upload Contract</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your contract here",
        type=["pdf", "docx"],
        help="Supported: PDF, DOCX",
        label_visibility="collapsed",
    )

    if not uploaded_file:
        st.markdown("""
        <div class="upload-hint">
            <div class="icon">📋</div>
            <strong>Upload a PDF or DOCX contract to begin analysis</strong>
            Drag & drop or click the button above · Max 200MB
        </div>
        """, unsafe_allow_html=True)

    if uploaded_file:
        if st.button("🚀 Analyze Contract", use_container_width=True):
            _run_analysis(uploaded_file, api_key, use_ai)

    # ── Results ─────────────────────────────────────────────────────────
    if st.session_state.analyzed_clauses:
        _render_results(filter_level, sort_by, api_key)


def _run_analysis(uploaded_file, api_key: str, use_ai: bool):
    """Run the full agentic analysis pipeline."""
    from core.extractor import extract_text_from_pdf, extract_text_from_docx, split_into_clauses
    from agents.agents import ClauseAnalysisAgent, RiskAnalysisAgent, ReportAgent
    from rag.rag_engine import get_rag_engine

    if use_ai and not api_key:
        st.warning("GEMINI_API_KEY is not configured. Continuing with heuristic analysis. Add your key to .env to enable Gemini.")
        use_ai = False
    client = get_gemini_client(api_key) if api_key and use_ai else None
    file_bytes = uploaded_file.read()

    progress = st.progress(0, text="📄 Extracting contract text...")

    # Phase 1: Extract text
    try:
        if uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        else:
            text = extract_text_from_docx(file_bytes)
    except Exception as e:
        st.error(f"Text extraction failed: {e}")
        return

    if len(text) < 100:
        st.error("Could not extract meaningful text from this file. Try a text-based PDF (not scanned).")
        return

    st.session_state.contract_text = text
    progress.progress(15, text="✂️ Splitting into clauses...")

    # Phase 2: Split clauses
    clauses = split_into_clauses(text)
    if not clauses:
        st.error("No clauses detected. The document may be too short or in an unsupported format.")
        return

    progress.progress(30, text=f"🏷️ Classifying {len(clauses)} clauses (Agent 1)...")

    # Phase 3: Clause Analysis Agent
    clause_agent = ClauseAnalysisAgent(client)
    classified = clause_agent.run(clauses, use_ai=use_ai)

    progress.progress(55, text="⚠️ Assessing risks with RAG context (Agent 2)...")

    # Phase 4: Initialize RAG
    try:
        rag = get_rag_engine()
        rag.initialize()
    except Exception as e:
        st.warning(f"RAG initialization issue (continuing with heuristics): {e}")

    # Phase 5: Risk Analysis Agent
    risk_agent = RiskAnalysisAgent(client)
    analyzed = risk_agent.run(classified, use_ai=use_ai)
    st.session_state.analyzed_clauses = analyzed

    progress.progress(85, text="📊 Generating contract summary (Agent 3)...")

    # Phase 6: Report Agent
    report_agent = ReportAgent(client)
    summary = report_agent.generate_summary(text, analyzed)
    st.session_state.summary = summary
    st.session_state.qa_history = []

    progress.progress(100, text="✅ Analysis complete!")
    import time; time.sleep(0.5)
    progress.empty()

    st.success(f"✅ Analysis complete — {len(analyzed)} clauses analyzed!")
    st.rerun()


def _render_results(filter_level: str, sort_by: str, api_key: str):
    """Render full analysis results."""
    clauses = st.session_state.analyzed_clauses
    summary = st.session_state.summary

    # ── Summary Card ─────────────────────────────────────────────────
    rc = summary.get("risk_counts", {})
    overall = summary.get("overall_risk", "Unknown")
    color = RISK_COLORS_HEX.get(overall, "#64748B")

    findings_html = "".join(
        f'<div class="finding-item">{f}</div>'
        for f in summary.get("key_findings", [])[:4]
    )

    st.markdown(f"""
    <div class="summary-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
                <h2>{summary.get('contract_type', 'Contract Analysis')}</h2>
                <div class="meta">Parties: {summary.get('parties', 'Not specified')}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Overall Risk</div>
                <div style="font-size:1.6rem;font-weight:800;color:{color};">{overall}</div>
            </div>
        </div>
        <div class="summary-findings">{findings_html}</div>
    </div>
    """, unsafe_allow_html=True)

    render_metric_grid(rc, summary.get("avg_score", 0))

    # ── Tabs ─────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Clause Analysis", "📊 Risk Overview", "💬 Contract Q&A", "📥 Download Report"
    ])

    with tab1:
        _render_clause_tab(clauses, filter_level, sort_by)

    with tab2:
        _render_risk_overview(clauses, summary)

    with tab3:
        _render_qa_tab(api_key)

    with tab4:
        _render_download_tab(summary, clauses)


def _render_clause_tab(clauses: list, filter_level: str, sort_by: str):
    # Filter
    if filter_level != "All":
        filtered = [c for c in clauses if c.get("risk_level") == filter_level]
    else:
        filtered = clauses

    # Sort
    if sort_by == "Risk Score ↓":
        filtered = sorted(filtered, key=lambda c: c.get("risk_score", 0), reverse=True)
    elif sort_by == "Risk Score ↑":
        filtered = sorted(filtered, key=lambda c: c.get("risk_score", 0))

    st.markdown(f'<div class="section-title">📋 Clause Analysis <span style="font-size:0.8rem;font-weight:400;color:var(--text-3);">({len(filtered)} clauses)</span></div>', unsafe_allow_html=True)

    if not filtered:
        st.info(f"No clauses found for risk level: {filter_level}")
        return

    for clause in filtered:
        render_clause_card(clause)


def _render_risk_overview(clauses: list, summary: dict):
    import pandas as pd

    st.markdown('<div class="section-title">📊 Risk Overview</div>', unsafe_allow_html=True)

    # Build data table
    rows = []
    for c in clauses:
        rows.append({
            "#": c.get("index"),
            "Heading": c.get("heading", "")[:60],
            "Type": c.get("type", ""),
            "Risk Level": c.get("risk_level", ""),
            "Score": c.get("risk_score", 0),
        })

    df = pd.DataFrame(rows)

    # Style the dataframe
    def color_risk(val):
        colors_map = {"Critical": "#FEF2F2", "High": "#FFF7ED", "Medium": "#FFFBEB", "Low": "#F0FDF4"}
        return f"background-color: {colors_map.get(val, 'white')}"

    st.dataframe(
        df.style.applymap(color_risk, subset=["Risk Level"]),
        use_container_width=True,
        height=400,
    )

    # Score distribution
    st.markdown("#### Score Distribution by Clause Type")
    type_scores = {}
    for c in clauses:
        t = c.get("type", "Other")
        s = c.get("risk_score", 0)
        type_scores.setdefault(t, []).append(s)

    type_avg = {t: sum(v)/len(v) for t, v in type_scores.items()}
    type_df = pd.DataFrame(
        sorted(type_avg.items(), key=lambda x: -x[1]),
        columns=["Clause Type", "Avg Risk Score"]
    )

    st.bar_chart(type_df.set_index("Clause Type"))

    # Recommendations
    recs = summary.get("recommendations", [])
    if recs:
        st.markdown("#### Recommendations")
        for r in recs:
            st.markdown(f"""
            <div class="info-box" style="margin-bottom:0.5rem;">→ {r}</div>
            """, unsafe_allow_html=True)


def _render_qa_tab(api_key: str):
    from rag.rag_engine import get_rag_engine

    st.markdown('<div class="section-title">💬 Ask About Your Contract</div>', unsafe_allow_html=True)

    if not st.session_state.contract_text:
        st.info("Upload and analyze a contract first.")
        return

    st.markdown("""
    <div class="info-box">
        Ask anything about your uploaded contract — payment terms, termination conditions,
        obligations, deadlines, or any clause you want clarified.
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.qa_history:
        role = msg["role"]
        content = msg["content"]
        label = "You" if role == "user" else "LexAI"
        label_cls = "user" if role == "user" else "assistant"
        st.markdown(f"""
        <div class="qa-bubble {label_cls}">
            <div class="qa-label {label_cls}">{label}</div>
            {content}
        </div>
        """, unsafe_allow_html=True)

    # Input
    question = st.text_input(
        "Your question",
        placeholder="e.g. What are the termination conditions? When is payment due?",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        send = st.button("Ask →", use_container_width=True)
    with col2:
        if st.button("Clear history", use_container_width=False):
            st.session_state.qa_history = []
            st.rerun()

    if send and question.strip() and api_key:
        st.session_state.qa_history.append({"role": "user", "content": question})
        with st.spinner("Analyzing contract..."):
            try:
                client = get_gemini_client(api_key)
                rag = get_rag_engine()
                answer = rag.answer_question(question, st.session_state.contract_text, client)
                st.session_state.qa_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.session_state.qa_history.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}"
                })
        st.rerun()
    elif send and not api_key:
        st.warning("Gemini API key is not configured in the .env file.")


def _render_download_tab(summary: dict, clauses: list):
    from reports.report_generator import generate_pdf_report

    st.markdown('<div class="section-title">📥 Download Report</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        Generate a professional PDF report containing the executive summary, risk distribution,
        and full clause-by-clause analysis with review points.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Report Preview")
    rc = summary.get("risk_counts", {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Contract Type", summary.get("contract_type", "N/A"))
        st.metric("Total Clauses", len(clauses))
        st.metric("Critical + High Risks", rc.get("Critical", 0) + rc.get("High", 0))
    with col2:
        st.metric("Overall Risk Level", summary.get("overall_risk", "N/A"))
        st.metric("Average Risk Score", f"{summary.get('avg_score', 0):.1f}/100")
        st.metric("Medium Risks", rc.get("Medium", 0))

    if st.button("📄 Generate PDF Report", use_container_width=True):
        with st.spinner("Building report..."):
            try:
                pdf_bytes = generate_pdf_report(summary, clauses)
                st.download_button(
                    label="⬇️ Download Contract Analysis Report (PDF)",
                    data=pdf_bytes,
                    file_name="contract_analysis_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.success("Report ready! Click the download button above.")
            except Exception as e:
                st.error(f"Report generation failed: {e}")


if __name__ == "__main__":
    main()