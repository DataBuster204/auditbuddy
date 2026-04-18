import os
import base64
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from parser import extract_text
from engine import (
    summarise,
    detect_red_flags,
    answer_question,
    generate_audit_memo,
    generate_custom_report,
    to_word_bytes,
)
from config_loader import load_config

load_dotenv()

# ── Load white-label config ───────────────────────────────────────────────
# All branding comes from config.yaml — no hardcoding needed
cfg      = load_config()
COMPANY  = cfg["company"]
COLORS   = cfg["colors"]

PRIMARY  = COLORS["primary"]
DARK     = COLORS["dark"]
DARK_MID = COLORS["dark_mid"]
LIGHT_BG = COLORS["light_bg"]
MUTED    = COLORS["text_muted"]


# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{COMPANY['name']} — {COMPANY['tagline']}",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Dynamic CSS ───────────────────────────────────────────────────────────
# We inject the config colors directly into CSS so the whole UI
# rebrands automatically when a client changes their config.yaml
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {DARK} 0%, {DARK_MID} 100%);
        border-right: 1px solid #1E3A5F;
    }}
    [data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] .stFileUploader {{
        background: #0F2040;
        border-radius: 10px;
        padding: 0.5rem;
        border: 1px dashed {PRIMARY};
    }}

    /* ── Brand header ── */
    .brand-header {{
        background: linear-gradient(135deg, {DARK} 0%, {DARK_MID} 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        border-left: 6px solid {PRIMARY};
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }}
    .brand-header h1 {{
        color: #FFFFFF;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    .brand-header p {{
        color: #AECFB8;
        margin: 0.4rem 0 0 0;
        font-size: 1rem;
    }}

    /* ── Stat cards ── */
    .stat-card {{
        background: #FFFFFF;
        border: 1px solid #E2F0E8;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}
    .stat-card .number {{
        font-size: 2rem;
        font-weight: 800;
        color: {PRIMARY};
    }}
    .stat-card .label {{
        font-size: 0.8rem;
        color: {MUTED};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ── Feature cards ── */
    .feature-card {{
        background: {LIGHT_BG};
        border: 1px solid #D1EDD8;
        border-top: 4px solid {PRIMARY};
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }}
    .feature-card:hover {{
        transform: translateY(-2px);
    }}
    .feature-card .icon {{
        font-size: 1.6rem;
        font-weight: 800;
        color: {PRIMARY};
        margin-bottom: 0.4rem;
    }}
    .feature-card strong {{
        color: #1E293B;
        font-size: 0.95rem;
    }}
    .feature-card p {{
        color: {MUTED};
        font-size: 0.82rem;
        margin-top: 0.3rem;
    }}

    /* ── Result box ── */
    .result-box {{
        background: #FFFFFF;
        border: 1px solid #E2F0E8;
        border-left: 5px solid {PRIMARY};
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-top: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }}

    /* ── Chat bubbles ── */
    .chat-user {{
        background: #EFF6FF;
        border-radius: 12px 12px 4px 12px;
        padding: 0.8rem 1.1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #3B82F6;
        font-size: 0.92rem;
    }}
    .chat-bot {{
        background: #F0FDF4;
        border-radius: 12px 12px 12px 4px;
        padding: 0.8rem 1.1rem;
        margin: 0.5rem 0;
        border-left: 3px solid {PRIMARY};
        font-size: 0.92rem;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: #F1F5F9;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-size: 0.88rem;
        color: {MUTED};
    }}
    .stTabs [aria-selected="true"] {{
        background: #FFFFFF !important;
        color: {DARK} !important;
        box-shadow: 0 1px 6px rgba(0,0,0,0.1);
    }}

    /* ── Buttons ── */
    .stButton button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }}
    .stButton button[kind="primary"] {{
        background: {PRIMARY} !important;
        color: {DARK} !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
    }}
    .stButton button[kind="primary"]:hover {{
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
    }}

    /* ── Download buttons ── */
    .stDownloadButton button {{
        background: transparent !important;
        color: {PRIMARY} !important;
        border: 2px solid {PRIMARY} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }}
    .stDownloadButton button:hover {{
        background: {PRIMARY} !important;
        color: {DARK} !important;
    }}

    /* ── Export label ── */
    .export-label {{
        font-size: 0.82rem;
        font-weight: 600;
        color: {MUTED};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}

    /* ── Section heading ── */
    .section-heading {{
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }}
    .section-caption {{
        font-size: 0.85rem;
        color: {MUTED};
        margin-bottom: 1rem;
    }}

    /* ── Info/success boxes ── */
    .stAlert {{
        border-radius: 10px !important;
    }}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────
if "doc_text" not in st.session_state:
    st.session_state.doc_text = None
if "doc_name" not in st.session_state:
    st.session_state.doc_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "summary_cache" not in st.session_state:
    st.session_state.summary_cache = None
if "flags_cache" not in st.session_state:
    st.session_state.flags_cache = None
if "memo_cache" not in st.session_state:
    st.session_state.memo_cache = None


# ── Export buttons helper ─────────────────────────────────────────────────
def export_buttons(content, label, doc_name, key_prefix):
    st.markdown('<p class="export-label">Export as</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download Word (.docx)",
            data=to_word_bytes(content, label),
            file_name=f"AuditBuddy_{key_prefix}_{doc_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"dl_{key_prefix}_docx",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download Markdown (.md)",
            data=content,
            file_name=f"AuditBuddy_{key_prefix}_{doc_name}.md",
            mime="text/markdown",
            key=f"dl_{key_prefix}_md",
            use_container_width=True,
        )
    with col3:
        st.download_button(
            "Download Text (.txt)",
            data=content,
            file_name=f"AuditBuddy_{key_prefix}_{doc_name}.txt",
            mime="text/plain",
            key=f"dl_{key_prefix}_txt",
            use_container_width=True,
        )


# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo
    logo_path = COMPANY.get("logo", "")
    if logo_path and Path(logo_path).exists():
        st.image(logo_path, use_container_width=True)
    else:
        default_logo = Path("assets/default_logo.svg")
        if default_logo.exists():
            svg_content = default_logo.read_text()
            b64 = base64.b64encode(svg_content.encode()).decode()
            st.markdown(
                f'<img src="data:image/svg+xml;base64,{b64}" style="width:100%; margin-bottom:0.5rem;">',
                unsafe_allow_html=True,
            )

    st.markdown(f"<p style='color:#AECFB8; font-size:0.8rem; margin-top:0.2rem;'>{COMPANY['tagline']}</p>", unsafe_allow_html=True)
    st.divider()

    # API Key
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Your key is never stored. Get one at platform.openai.com",
        placeholder="sk-...",
    )

    st.divider()

    # File upload
    st.markdown("**Upload Document**")
    st.caption("PDF, Excel (.xlsx) or Word (.docx)")
    uploaded = st.file_uploader(
        "upload",
        type=["pdf", "xlsx", "xls", "docx"],
        label_visibility="collapsed",
    )

    if uploaded:
        with st.spinner("Parsing document..."):
            try:
                text, ftype = extract_text(uploaded)
                st.session_state.doc_text = text
                st.session_state.doc_name = uploaded.name
                st.session_state.summary_cache = None
                st.session_state.flags_cache   = None
                st.session_state.memo_cache    = None
                st.session_state.chat_history  = []
                st.success(f"{ftype} parsed successfully")
            except Exception as e:
                st.error(f"Parse error: {e}")

    st.divider()

    if st.session_state.doc_text:
        st.markdown("**Active Document**")
        st.markdown(f"`{st.session_state.doc_name}`")
        word_count = len(st.session_state.doc_text.split())
        st.caption(f"{word_count:,} words extracted")

        # Mini stats
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Words", f"{word_count:,}")
        with c2:
            chars = len(st.session_state.doc_text)
            st.metric("Chars", f"{chars:,}")

        st.button(
            "Clear Document",
            use_container_width=True,
            key="clear_doc",
            on_click=lambda: [
                st.session_state.update({
                    "doc_text": None,
                    "doc_name": None,
                    "summary_cache": None,
                    "flags_cache": None,
                    "memo_cache": None,
                    "chat_history": [],
                })
            ]
        )
    else:
        st.info("No document loaded. Upload one above to begin.")

    st.divider()
    st.caption(f"Built by [{COMPANY['built_by']}](https://{COMPANY['website']})")
    st.caption("Powered by GPT-4o-mini and LangChain")


# ── Main area ─────────────────────────────────────────────────────────────

# Brand header
st.markdown(f"""
<div class="brand-header">
    <h1>📊 {COMPANY['name']}</h1>
    <p>{COMPANY['tagline']} — Upload a financial document and get AI-powered insights in seconds.</p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.warning("Enter your OpenAI API key in the sidebar to get started.")
    st.stop()

if not st.session_state.doc_text:

    # Feature grid
    st.markdown("### What you can do with AuditBuddy")
    st.markdown(" ")
    cols = st.columns(3)
    features = [
        ("01", "Summarise Documents", "Plain-English breakdown of any financial statement — figures, ratios, and key takeaways."),
        ("02", "Flag Risks", "AI spots red flags, anomalies, and concerning trends before they become problems."),
        ("03", "Ask Questions", "Chat directly with your document — ask anything about the numbers."),
        ("04", "Audit Memo", "Generate a board-ready audit observation memo in one click."),
        ("05", "Custom Reports", "Describe the analysis you need and get a structured report instantly."),
        ("06", "Multi-format", "Works with PDF, Excel, and Word — the formats finance actually uses."),
    ]
    for i, (num, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="icon">{num}</div>
                <strong>{title}</strong>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(" ")
    st.info("Upload a financial document in the sidebar to begin your analysis.")
    st.stop()


# ── Document loaded — show stats bar ─────────────────────────────────────
word_count = len(st.session_state.doc_text.split())
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="number">{word_count:,}</div>
        <div class="label">Words Extracted</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="number">5</div>
        <div class="label">AI Tools Ready</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="number">3</div>
        <div class="label">Export Formats</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="number">GPT-4o</div>
        <div class="label">AI Model</div>
    </div>""", unsafe_allow_html=True)

st.markdown(" ")


# ── Tabs ──────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Summary",
    "Red Flags",
    "Q&A Chat",
    "Audit Memo",
    "Custom Report",
])


# ── Tab 1: Summary ────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<p class="section-heading">Document Summary</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-caption">Plain-English breakdown of the key figures and financial position.</p>', unsafe_allow_html=True)

    if st.button("Generate Summary", type="primary", use_container_width=True, key="gen_summary"):
        with st.spinner("Analysing your document..."):
            try:
                result = summarise(st.session_state.doc_text, api_key)
                st.session_state.summary_cache = result
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.summary_cache:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.summary_cache)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(" ")
        export_buttons(
            st.session_state.summary_cache,
            "AuditBuddy - Document Summary",
            st.session_state.doc_name,
            "summary",
        )


# ── Tab 2: Red Flags ──────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<p class="section-heading">Red Flag and Risk Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-caption">AI-powered forensic review — flags anomalies, risks, and areas needing attention.</p>', unsafe_allow_html=True)

    if st.button("Detect Red Flags", type="primary", use_container_width=True, key="gen_flags"):
        with st.spinner("Running forensic analysis..."):
            try:
                result = detect_red_flags(st.session_state.doc_text, api_key)
                st.session_state.flags_cache = result
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.flags_cache:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.flags_cache)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(" ")
        export_buttons(
            st.session_state.flags_cache,
            "AuditBuddy - Risk Analysis",
            st.session_state.doc_name,
            "flags",
        )


# ── Tab 3: Q&A Chat ───────────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<p class="section-heading">Ask Your Document</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-caption">Ask any question and get a grounded, cited answer straight from the document.</p>', unsafe_allow_html=True)

    with st.expander("Suggested questions", expanded=False):
        suggested = [
            "What is the net profit margin?",
            "What are the total liabilities?",
            "Is this business profitable?",
            "What is the current ratio?",
            "What are the top 3 expense categories?",
            "How does revenue compare to last period?",
        ]
        cols = st.columns(2)
        for i, q in enumerate(suggested):
            with cols[i % 2]:
                if st.button(q, key=f"sugg_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    with st.spinner("Thinking..."):
                        try:
                            answer = answer_question(st.session_state.doc_text, q, api_key)
                            st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        except Exception as e:
                            st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {e}"})

    st.markdown(" ")

    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot"><strong>AuditBuddy:</strong></div>', unsafe_allow_html=True)
                st.markdown(msg["content"])
        st.markdown(" ")
        if st.button("Clear chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.info("Ask a question about your document below.")

    st.divider()
    with st.form("chat_form", clear_on_submit=True):
        user_q = st.text_input(
            "Your question:",
            placeholder="e.g. What is the total revenue for this period?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send", type="primary")

    if submitted and user_q.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        with st.spinner("Analysing..."):
            try:
                answer = answer_question(st.session_state.doc_text, user_q, api_key)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {e}"})
        st.rerun()


# ── Tab 4: Audit Memo ─────────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<p class="section-heading">Audit Observation Memo</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-caption">Generate a board-ready formal memo structured for management distribution.</p>', unsafe_allow_html=True)

    st.info("This generates a structured Audit Observation Memo with findings, risk levels, and recommended actions.")

    if st.button("Generate Audit Memo", type="primary", use_container_width=True, key="gen_memo"):
        with st.spinner("Drafting your audit memo..."):
            try:
                result = generate_audit_memo(st.session_state.doc_text, api_key)
                st.session_state.memo_cache = result
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.memo_cache:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.memo_cache)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(" ")
        export_buttons(
            st.session_state.memo_cache,
            "AuditBuddy - Audit Observation Memo",
            st.session_state.doc_name,
            "memo",
        )


# ── Tab 5: Custom Report ──────────────────────────────────────────────────
with tabs[4]:
    st.markdown('<p class="section-heading">Custom Analysis and Report Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-caption">Describe exactly what you need — AuditBuddy will generate a tailored report instantly.</p>', unsafe_allow_html=True)

    with st.expander("Report templates", expanded=False):
        templates = {
            "Working Capital Analysis": "Perform a working capital analysis. Calculate and interpret the current ratio, quick ratio, and cash conversion cycle.",
            "Profitability Deep Dive": "Analyse the profitability of this business. Cover gross margin, operating margin, net margin, and EBITDA if available.",
            "Expense Breakdown": "Break down all expense categories, rank them by size, calculate each as a percentage of revenue, and flag any that appear unusually high.",
            "Cash Flow Assessment": "Assess the cash position and cash flow health of this business. Identify any liquidity risks.",
            "Year-on-Year Comparison": "If multiple periods are present, perform a year-on-year comparison and highlight significant changes.",
        }
        selected = st.selectbox("Choose a template:", ["(none)"] + list(templates.keys()))

    prompt_value = templates.get(selected, "") if selected != "(none)" else ""

    with st.form("report_form"):
        custom_prompt = st.text_area(
            "Describe your analysis request:",
            value=prompt_value,
            height=130,
            placeholder="e.g. Perform a detailed working capital analysis and flag any liquidity risks...",
        )
        run_report = st.form_submit_button("Generate Report", type="primary")

    if run_report and custom_prompt.strip():
        with st.spinner("Generating your custom report..."):
            try:
                result = generate_custom_report(st.session_state.doc_text, custom_prompt, api_key)
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(" ")
                export_buttons(
                    result,
                    "AuditBuddy - Custom Report",
                    st.session_state.doc_name,
                    "report",
                )
            except Exception as e:
                st.error(f"Error: {e}")
    elif run_report:
        st.warning("Please enter an analysis request.")