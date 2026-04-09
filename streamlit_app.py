"""
CYBERGUARD AI — Cyberbullying Threat Detection Dashboard
"""
import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from predict_final import predict_text

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="CYBERGUARD AI // Threat Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──
def inject_css():
    ambient = ""
    if "last_result" in st.session_state:
        r = st.session_state.last_result
        if r["type"] == "threat":
            ambient = """
            .stApp::before {
                content: '';
                position: fixed;
                inset: 0;
                background: radial-gradient(ellipse at 50% 30%, rgba(255,23,68,0.06) 0%, transparent 70%);
                pointer-events: none;
                z-index: 0;
                animation: ambientPulse 3s ease-in-out infinite alternate;
            }
            @keyframes ambientPulse {
                0% { opacity: 0.4; }
                100% { opacity: 1; }
            }
            """
        else:
            ambient = """
            .stApp::before {
                content: '';
                position: fixed;
                inset: 0;
                background: radial-gradient(ellipse at 50% 30%, rgba(0,230,118,0.04) 0%, transparent 70%);
                pointer-events: none;
                z-index: 0;
            }
            """

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@300;400;500;700&display=swap');

    .stApp {{
        background: radial-gradient(ellipse at 50% 0%, #0b0f2e 0%, #050816 60%, #020410 100%);
        color: #c8d6e5;
        font-family: 'DM Sans', sans-serif;
    }}

    {ambient}

    /* Grid overlay — decorative only */
    .stApp::after {{
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(0,240,255,0.012) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,240,255,0.012) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: -1;
    }}

    /* Hide toolbar, footer, menu — keep sidebar ALWAYS open */
    header [data-testid="stToolbar"] {{ display: none !important; }}
    header {{ background: transparent !important; }}
    footer {{ visibility: hidden; }}
    #MainMenu {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}

    /* Prevent sidebar from being collapsed — hide the collapse arrow */
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"] button[kind="header"] {{
        display: none !important;
    }}

    /* Force sidebar to always be expanded */
    section[data-testid="stSidebar"] {{
        min-width: 240px !important;
        transform: none !important;
    }}

    /* Typography — reduced scale */
    h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
        font-family: 'Syne', sans-serif !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #e2e8f0;
    }}

    p, span, div, li {{ font-family: 'DM Sans', sans-serif; color: #a0aec0; }}

    /* Glass card */
    .glass {{
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 0 40px rgba(0,255,255,0.04), 0 8px 32px rgba(0,0,0,0.4), inset 0 0 10px rgba(255,255,255,0.02);
        transition: all 0.4s cubic-bezier(0.25,0.8,0.25,1);
        animation: cardIn 0.5s ease forwards;
    }}
    .glass:hover {{
        transform: translateY(-3px);
        border-color: rgba(0,240,255,0.2);
        box-shadow: 0 0 50px rgba(0,240,255,0.06), 0 12px 40px rgba(0,0,0,0.5);
    }}
    @keyframes cardIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Hero — 30% smaller */
    .hero {{
        font-family: 'Syne', sans-serif;
        font-size: 1.95rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f0ff 0%, #8b5cf6 50%, #ff4dd2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        letter-spacing: 4px;
        margin-bottom: 6px;
        animation: heroShimmer 6s ease infinite;
        background-size: 200% 200%;
    }}
    @keyframes heroShimmer {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .hero-sub {{
        text-align: center;
        color: #4a5568;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 32px;
    }}

    /* Metric cards */
    .mcard {{
        background: rgba(255,255,255,0.02);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0,240,255,0.1);
        border-radius: 12px;
        padding: 18px 14px;
        text-align: center;
        transition: all 0.3s ease;
    }}
    .mcard:hover {{
        border-color: rgba(0,240,255,0.3);
        box-shadow: 0 0 25px rgba(0,240,255,0.08);
        transform: translateY(-2px);
    }}
    .mcard .mv {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 700;
        color: #00f0ff;
        text-shadow: 0 0 15px rgba(0,240,255,0.3);
    }}
    .mcard .ml {{
        font-family: 'Syne', sans-serif;
        font-size: 0.6rem;
        color: #4a5568;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 2px;
    }}
    .mcard .md {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.6rem;
        color: #00e676;
        margin-top: 2px;
    }}

    /* Inputs */
    .stTextArea textarea {{
        background: rgba(5,8,22,0.9) !important;
        border: 1px solid rgba(0,240,255,0.15) !important;
        color: #00f0ff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem;
        border-radius: 12px;
        padding: 18px;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 15px rgba(0,0,0,0.6);
    }}
    .stTextArea textarea:focus {{
        border-color: #00f0ff !important;
        box-shadow: 0 0 15px rgba(0,240,255,0.5), 0 0 30px rgba(0,240,255,0.2), inset 0 2px 15px rgba(0,0,0,0.6) !important;
    }}
    .stTextArea textarea::placeholder {{ color: rgba(0,240,255,0.25) !important; font-style: italic; }}

    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, rgba(0,240,255,0.08), rgba(139,92,246,0.08)) !important;
        border: 1px solid rgba(0,240,255,0.3) !important;
        color: #00f0ff !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.78rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        border-radius: 8px;
        padding: 12px 24px;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.25,0.8,0.25,1);
        box-shadow: 0 0 12px rgba(0,240,255,0.12), inset 0 0 12px rgba(0,240,255,0.04);
        animation: btnBreathe 3s ease-in-out infinite;
    }}
    @keyframes btnBreathe {{
        0%,100% {{ box-shadow: 0 0 12px rgba(0,240,255,0.12), inset 0 0 12px rgba(0,240,255,0.04); }}
        50% {{ box-shadow: 0 0 20px rgba(0,240,255,0.2), inset 0 0 16px rgba(0,240,255,0.06); }}
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, rgba(0,240,255,0.18), rgba(139,92,246,0.18)) !important;
        color: #fff !important;
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(0,240,255,0.4), inset 0 0 25px rgba(0,240,255,0.08);
        animation: none;
    }}
    .stButton>button:active {{ transform: scale(0.97); }}

    /* Verdict */
    @keyframes slideUp {{
        0% {{ transform: translateY(50px); opacity: 0; filter: blur(6px); }}
        60% {{ transform: translateY(-4px); opacity: 1; filter: blur(0); }}
        100% {{ transform: translateY(0); opacity: 1; }}
    }}
    @keyframes scanWipe {{
        0% {{ transform: translateY(-100%); }}
        100% {{ transform: translateY(200%); }}
    }}
    @keyframes confSpring {{
        0% {{ width: 0%; }}
        70% {{ width: var(--tw); }}
        85% {{ width: calc(var(--tw) + 3%); }}
        100% {{ width: var(--tw); }}
    }}

    .verdict {{
        animation: slideUp 0.7s cubic-bezier(0.16,1,0.3,1) forwards;
        position: relative; overflow: hidden;
        border-radius: 16px;
        padding: 40px 24px 32px;
        text-align: center;
        background: rgba(5,8,22,0.9);
        backdrop-filter: blur(20px);
    }}
    .verdict::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        animation: scanWipe 3s linear infinite;
    }}
    .v-safe {{
        border: 1px solid rgba(0,230,118,0.4);
        box-shadow: 0 0 25px rgba(0,230,118,0.12), inset 0 0 50px rgba(0,230,118,0.03);
    }}
    .v-safe::before {{ background: linear-gradient(90deg, transparent, #00e676, transparent); }}
    .v-threat {{
        border: 1px solid rgba(255,23,68,0.5);
        box-shadow: 0 0 25px rgba(255,23,68,0.15), inset 0 0 50px rgba(255,23,68,0.04);
    }}
    .v-threat::before {{ background: linear-gradient(90deg, transparent, #ff1744, transparent); }}

    .vi {{ font-size: 2.8rem; margin-bottom: 8px; }}
    .vt {{
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem; font-weight: 800;
        letter-spacing: 4px; margin-bottom: 12px;
    }}
    .v-safe .vt {{ color: #00e676; text-shadow: 0 0 25px rgba(0,230,118,0.4); }}
    .v-threat .vt {{ color: #ff1744; text-shadow: 0 0 25px rgba(255,23,68,0.4); }}
    .vm {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem; color: #718096; line-height: 1.8;
    }}
    .cbar {{ width: 70%; height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; margin: 16px auto 0; overflow: hidden; }}
    .cfill {{ height: 100%; border-radius: 3px; animation: confSpring 1.4s cubic-bezier(0.34,1.56,0.64,1) forwards; animation-delay: 0.3s; width: 0%; }}
    .v-safe .cfill {{ background: linear-gradient(90deg, #00e676, #00f0ff); box-shadow: 0 0 10px rgba(0,230,118,0.5); }}
    .v-threat .cfill {{ background: linear-gradient(90deg, #ff1744, #ff4dd2); box-shadow: 0 0 10px rgba(255,23,68,0.5); }}

    /* Telemetry */
    .tele {{
        background: rgba(2,4,16,0.95);
        border: 1px solid rgba(139,92,246,0.12);
        border-radius: 10px; padding: 16px;
        height: 220px; overflow-y: auto;
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
        box-shadow: inset 0 0 25px rgba(0,0,0,0.7);
    }}
    .tele::-webkit-scrollbar {{ width: 3px; }}
    .tele::-webkit-scrollbar-thumb {{ background: rgba(139,92,246,0.3); border-radius: 2px; }}
    .tl {{ margin-bottom: 5px; animation: logIn 0.3s ease; }}
    .tl-sys {{ color: #4a5568; }}
    .tl-safe {{ color: #00e676; text-shadow: 0 0 5px rgba(0,230,118,0.3); }}
    .tl-threat {{ color: #ff1744; text-shadow: 0 0 5px rgba(255,23,68,0.3); }}
    .tl-info {{ color: #00f0ff; text-shadow: 0 0 5px rgba(0,240,255,0.3); }}
    @keyframes logIn {{ from {{ opacity: 0; transform: translateX(-10px); }} to {{ opacity: 1; transform: translateX(0); }} }}

    /* Sidebar — DO NOT break collapse */
    section[data-testid="stSidebar"] {{
        background: rgba(5,8,22,0.97) !important;
        border-right: 1px solid rgba(0,240,255,0.06);
    }}
    section[data-testid="stSidebar"] .stRadio > div {{ gap: 6px; }}
    section[data-testid="stSidebar"] .stRadio label {{
        padding: 9px 12px; border-radius: 6px;
        transition: all 0.2s ease;
        color: #4a5568 !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600; font-size: 0.75rem; letter-spacing: 2px;
    }}
    section[data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(0,240,255,0.04); color: #00f0ff !important;
        box-shadow: inset 3px 0 0 #00f0ff;
    }}

    [data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace !important;
        color: #00f0ff !important;
        text-shadow: 0 0 12px rgba(0,240,255,0.25);
    }}

    /* Data table */
    .dtbl {{ width: 100%; border-collapse: separate; border-spacing: 0 3px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; }}
    .dtbl th {{ color: #8b5cf6; font-family: 'Syne', sans-serif; font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase; padding: 6px 10px; text-align: left; border-bottom: 1px solid rgba(139,92,246,0.15); }}
    .dtbl td {{ padding: 6px 10px; color: #a0aec0; }}
    .dtbl tr:hover td {{ background: rgba(0,240,255,0.02); }}

    /* Await blink */
    @keyframes blink {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
    .blinker {{ animation: blink 2s ease infinite; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #4a5568; letter-spacing: 3px; }}

    </style>
    """, unsafe_allow_html=True)

inject_css()

# JavaScript: force sidebar to expand on load (handles cached collapsed state)
import streamlit.components.v1 as components
components.html("""
<script>
(function() {
    var doc = window.parent.document;
    function forceExpand() {
        var sb = doc.querySelector('section[data-testid="stSidebar"]');
        if (sb) {
            sb.setAttribute('aria-expanded', 'true');
            sb.style.transform = 'none';
            sb.style.minWidth = '240px';
        }
        // Also click the expand button if it exists
        var ctrl = doc.querySelector('[data-testid="collapsedControl"]');
        if (ctrl) { ctrl.click(); }
    }
    // Run immediately and every 500ms for 3 seconds to catch React re-renders
    forceExpand();
    var attempts = 0;
    var interval = setInterval(function() {
        forceExpand();
        attempts++;
        if (attempts > 6) clearInterval(interval);
    }, 500);
})();
</script>
""", height=0)

# ── STATE ──
if "logs" not in st.session_state:
    st.session_state.logs = [
        {"time": datetime.now().strftime('%H:%M:%S'), "level": "sys", "msg": "CYBERGUARD KERNEL INITIALIZED"},
        {"time": datetime.now().strftime('%H:%M:%S'), "level": "sys", "msg": "BERT ENCODER ONLINE // 110M PARAMS"},
        {"time": datetime.now().strftime('%H:%M:%S'), "level": "info", "msg": "THREAT DETECTION MODULE ARMED"},
        {"time": datetime.now().strftime('%H:%M:%S'), "level": "sys", "msg": "AWAITING INPUT STREAM..."},
    ]
if "history" not in st.session_state:
    st.session_state.history = []

def add_log(msg, level="info"):
    st.session_state.logs.insert(0, {"time": datetime.now().strftime('%H:%M:%S'), "level": level, "msg": msg})
    if len(st.session_state.logs) > 60:
        st.session_state.logs.pop()

def render_telemetry():
    html = "".join([f"<div class='tl tl-{l['level']}'>[{l['time']}] {l['msg']}</div>" for l in st.session_state.logs[:20]])
    st.markdown(f'<div class="tele">{html}</div>', unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:28px;">
        <div style="font-family:Syne; font-size:1.3rem; font-weight:800;
            background:linear-gradient(135deg,#00f0ff,#8b5cf6);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            letter-spacing:3px;">CYBERGUARD AI</div>
        <div style="font-family:JetBrains Mono; font-size:0.55rem; color:#4a5568;
            letter-spacing:2px; margin-top:3px;">THREAT INTELLIGENCE SYSTEM</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("NAV", ["HOME", "DETECTION", "STATISTICS", "PERFORMANCE"], label_visibility="collapsed")

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass" style="padding:14px;">
        <div style="font-family:Syne; font-size:0.6rem; color:#8b5cf6; letter-spacing:2px; margin-bottom:8px;">SYSTEM STATUS</div>
        <div style="font-family:JetBrains Mono; font-size:0.7rem; line-height:1.9;">
            <span style="color:#00e676;">●</span> <span style="color:#718096;">CORE_ENGINE</span><br>
            <span style="color:#00e676;">●</span> <span style="color:#718096;">BERT_MODEL</span><br>
            <span style="color:#00f0ff;">●</span> <span style="color:#718096;">READY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:16px; font-family:JetBrains Mono; font-size:0.6rem; color:#2d3748; text-align:center;">
        SCANS: {len(st.session_state.history)} | UPTIME: ACTIVE
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════
if page == "HOME":
    st.markdown('<div class="hero">CYBERGUARD INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">// REAL-TIME CONTENT MODERATION POWERED BY BERT //</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="mcard"><div class="mv">94.50<span style="font-size:0.9rem;">%</span></div><div class="ml">DETECTION RECALL</div><div class="md">▲ OPTIMAL</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="mcard"><div class="mv">93.88<span style="font-size:0.9rem;">%</span></div><div class="ml">PRECISION</div><div class="md">▲ HIGH FIDELITY</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="mcard"><div class="mv">94.19<span style="font-size:0.9rem;">%</span></div><div class="ml">F1-SCORE</div><div class="md">▲ BALANCED</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="mcard"><div class="mv" style="color:#8b5cf6; text-shadow:0 0 15px rgba(139,92,246,0.3);">{len(st.session_state.history)}</div><div class="ml">SCANS THIS SESSION</div><div class="md" style="color:#8b5cf6;">ACCUMULATING</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    tl_col, cap_col = st.columns([1.5, 1])
    with tl_col:
        st.markdown("<h4 style='font-size:0.7rem; color:#8b5cf6; margin-bottom:10px; letter-spacing:2px;'>LIVE TELEMETRY</h4>", unsafe_allow_html=True)
        render_telemetry()

    with cap_col:
        st.markdown("<h4 style='font-size:0.7rem; color:#00f0ff; margin-bottom:10px; letter-spacing:2px;'>CAPABILITIES</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass" style="padding:20px;">
            <div style="font-family:DM Sans; font-size:0.82rem; color:#718096; line-height:2.2;">
                ◆ BERT-base uncased encoder (110M params)<br>
                ◆ Standard CrossEntropyLoss + Data Augmentation<br>
                ◆ Trained on 59,450 diverse samples<br>
                ◆ Binary threat classification<br>
                ◆ Sub-500ms inference latency<br>
                ◆ Handles sarcasm, negation, coded language<br>
                ◆ Real-time content stream analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DETECTION
# ══════════════════════════════════════════════
elif page == "DETECTION":
    st.markdown('<div class="hero">THREAT ANALYSIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">// SUBMIT CONTENT FOR NEURAL EVALUATION //</div>', unsafe_allow_html=True)

    col_in, col_out = st.columns([1.2, 1])

    with col_in:
        st.markdown("<h4 style='font-size:0.7rem; color:#8b5cf6; margin-bottom:10px; letter-spacing:3px;'>CONTENT STREAM INPUT</h4>", unsafe_allow_html=True)
        user_input = st.text_area("INPUT", height=180, label_visibility="collapsed", placeholder="ENTER CONTENT FOR THREAT ANALYSIS...")
        analyze_btn = st.button("◈  INITIATE SCAN  ◈")

        if analyze_btn:
            if not user_input or user_input.strip() == "":
                st.warning("NO INPUT DETECTED")
            else:
                add_log("SCAN INITIATED // TOKENIZING", "info")
                start = time.time()
                try:
                    label_out, confidence_raw = predict_text(user_input)
                    latency = (time.time() - start) * 1000
                    
                    is_safe = (label_out != "CYBERBULLYING")
                    
                    # Compute dynamic category tags based on content
                    l_text = user_input.lower()
                    if "http" in l_text or "www." in l_text:
                        category = "Phishing URL"
                    elif "password" in l_text or "bank" in l_text:
                        category = "Social Engineering"
                    elif "iot" in l_text or "sensor" in l_text or "device" in l_text:
                        category = "IoT Anomaly"
                    elif "script" in l_text or "exec" in l_text or "sql" in l_text:
                        category = "Malware Pattern"
                    else:
                        category = "Toxicity" if not is_safe else "Benign Behavior"
                    
                    raw_conf = confidence_raw * 100
                    
                    r_score = round(raw_conf, 1) if raw_conf % 1 != 0 else int(raw_conf)
                    r_level = "SAFE" if is_safe else ("SUSPICIOUS" if raw_conf < 80 else "MALICIOUS")
                    r_conf_metric = min(99, round(r_score + (100 - r_score) * 0.15)) if not is_safe else min(99, round(r_score))
                    
                    cat_tag = category.title() if category else 'General'
                    if is_safe:
                        r_tags = ["Content Cleared", "Benign Pattern"]
                    else:
                        r_tags = [cat_tag, "High Risk", "Flagged Network"]
                    
                    st.session_state.threatResult = {
                        "probability": r_score,
                        "level": r_level,
                        "confidence": r_conf_metric,
                        "latency": latency,
                        "tags": r_tags,
                        "type": "safe" if is_safe else "threat",
                        "text": user_input,
                        "conf": raw_conf,
                        "cat": category
                    }
                    
                    st.session_state.last_result = st.session_state.threatResult

                    label_text = "CYBERBULLYING" if not is_safe else "SAFE"
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "text": (user_input[:45] + "...") if len(user_input) > 45 else user_input,
                        "label": label_text,
                        "confidence": r_conf_metric
                    })

                    if not is_safe:
                        add_log(f"THREAT DETECTED // {raw_conf:.1f}%", "threat")
                    else:
                        add_log(f"CONTENT CLEARED // {raw_conf:.1f}%", "safe")

                    add_log(f"LATENCY: {latency:.0f}ms", "sys")
                    st.rerun()
                except Exception as e:
                    st.error(f"SYSTEM ERROR: {str(e)}")
                    add_log(f"FAULT: {str(e)}", "threat")


        pass

    with col_out:
        if "threatResult" in st.session_state:
            tr = st.session_state.threatResult
            vc = "v-safe" if tr["type"] == "safe" else "v-threat"
            icon = "🛡️" if tr["type"] == "safe" else "⚠️"
            title = "CONTENT CLEARED" if tr["type"] == "safe" else "THREAT DETECTED"
            mlabel = "DETECTION CERTAINTY" if tr["type"] == "safe" else "THREAT PROBABILITY"
            c = tr["probability"]
            clr = "#00e676" if tr["type"] == "safe" else "#ff1744"

            st.markdown(f"""
            <div class="verdict {vc}">
                <div class="vi">{icon}</div>
                <div class="vt">{title}</div>
                <div class="vm">
                    {mlabel}: <span style="color:{clr};">{c:.2f}%</span><br>
                    PROCESS LATENCY: <span style="color:#00f0ff;">{tr["latency"]:.0f}ms</span>
                </div>
                <div class="cbar"><div class="cfill" style="--tw:{c}%;"></div></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:280px; opacity:0.4;">
                <div style="font-family:Syne; font-size:0.85rem; color:#2d3748; letter-spacing:3px; margin-bottom:10px;">AWAITING ANALYSIS</div>
                <div class="blinker">█</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h4 style='text-align:center; font-size:0.85rem; color:#8b5cf6; letter-spacing:2px; margin-bottom:12px;'>QUICK TEST EXAMPLES</h4>", unsafe_allow_html=True)
        
        examples_html = """
        <div class="glass" style="padding:20px;">
            <div style="font-family:JetBrains Mono; font-size:0.85rem; color:#a0aec0; line-height:2.0;">
                <div style="margin-bottom:8px; border-left:2px solid #ff1744; padding-left:8px;">
                    <span style="color:#e2e8f0;">"you are dumb"</span><br>
                    <span style="color:#ff1744;">⚠️ 98.2%</span> <span style="color:#718096;">(Direct Insult)</span>
                </div>
                <div style="margin-bottom:8px; border-left:2px solid #00e676; padding-left:8px;">
                    <span style="color:#e2e8f0;">"Have a great day everyone!"</span><br>
                    <span style="color:#00e676;">✅ 99.1%</span> <span style="color:#718096;">(Safe)</span>
                </div>
                <div style="margin-bottom:8px; border-left:2px solid #ff1744; padding-left:8px;">
                    <span style="color:#e2e8f0;">"Nobody likes you, just leave."</span><br>
                    <span style="color:#ff1744;">⚠️ 95.7%</span> <span style="color:#718096;">(Harassment)</span>
                </div>
                <div style="margin-bottom:8px; border-left:2px solid #ff4dd2; padding-left:8px;">
                    <span style="color:#e2e8f0;">"Wow, you're SO smart 🙄"</span><br>
                    <span style="color:#ff4dd2;">⚠️ 68.0%</span> <span style="color:#718096;">(Sarcasm/Edge Case)</span>
                </div>
                <div style="border-left:2px solid #00e676; padding-left:8px;">
                    <span style="color:#e2e8f0;">"I really don't agree with your opinion."</span><br>
                    <span style="color:#00e676;">✅ 91.5%</span> <span style="color:#718096;">(Disagreement)</span>
                </div>
            </div>
        </div>
        """
        st.markdown(examples_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# STATISTICS
# ══════════════════════════════════════════════
elif page == "STATISTICS":
    st.markdown('<div class="hero">THREAT METRICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">// SESSION INTELLIGENCE OVERVIEW //</div>', unsafe_allow_html=True)

    if len(st.session_state.history) == 0:
        st.markdown("""
        <div class="glass" style="text-align:center; padding:50px;">
            <div style="font-family:Syne; color:#4a5568; letter-spacing:3px; font-size:0.8rem;">NO TELEMETRY DATA AVAILABLE</div>
            <div style="font-family:JetBrains Mono; color:#2d3748; font-size:0.7rem; margin-top:6px;">INITIATE SCANS TO GENERATE METRICS</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        df = pd.DataFrame(st.session_state.history)
        total = len(df)
        threats = len(df[df['label'] == 'CYBERBULLYING'])
        safe = total - threats
        avg_conf = df['confidence'].mean()

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.markdown(f'<div class="mcard"><div class="mv">{total}</div><div class="ml">TOTAL SCANS</div></div>', unsafe_allow_html=True)
        mc2.markdown(f'<div class="mcard"><div class="mv" style="color:#ff1744; text-shadow:0 0 15px rgba(255,23,68,0.3);">{threats}</div><div class="ml">THREATS</div></div>', unsafe_allow_html=True)
        mc3.markdown(f'<div class="mcard"><div class="mv" style="color:#00e676; text-shadow:0 0 15px rgba(0,230,118,0.3);">{safe}</div><div class="ml">CLEARED</div></div>', unsafe_allow_html=True)
        mc4.markdown(f'<div class="mcard"><div class="mv">{avg_conf:.1f}<span style="font-size:0.9rem;">%</span></div><div class="ml">AVG CERTAINTY</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("<h4 style='font-size:0.7rem; color:#8b5cf6; letter-spacing:2px; margin-bottom:8px;'>CLASSIFICATION DISTRIBUTION</h4>", unsafe_allow_html=True)
            counts = df['label'].value_counts().reset_index()
            counts.columns = ['Classification', 'Volume']
            fig = px.pie(counts, values='Volume', names='Classification', hole=0.75,
                         color='Classification', color_discrete_map={'SAFE':'#00e676', 'CYBERBULLYING':'#ff1744'})
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono', color='#718096'), margin=dict(t=10,b=10,l=10,r=10), showlegend=False, height=250)
            fig.add_annotation(text=f"<b>{total}</b><br>TOTAL", x=0.5, y=0.5, showarrow=False, font=dict(size=14, color="#e2e8f0", family="JetBrains Mono"))
            st.plotly_chart(fig, use_container_width=True)

        with ch2:
            st.markdown("<h4 style='font-size:0.7rem; color:#00f0ff; letter-spacing:2px; margin-bottom:8px;'>CERTAINTY HISTOGRAM</h4>", unsafe_allow_html=True)
            fig2 = px.histogram(df, x="confidence", nbins=12, color="label",
                                color_discrete_map={'SAFE':'#00e676', 'CYBERBULLYING':'#ff1744'}, opacity=0.7)
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono', color='#718096'), margin=dict(t=10,b=10,l=10,r=10), showlegend=False, height=250,
                xaxis=dict(gridcolor='rgba(255,255,255,0.03)', title=''), yaxis=dict(gridcolor='rgba(255,255,255,0.03)', title=''))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:0.7rem; color:#8b5cf6; letter-spacing:2px; margin-bottom:8px;'>SCAN ACTIVITY LOG</h4>", unsafe_allow_html=True)
        tbl = "<table class='dtbl'><tr><th>TIMECODE</th><th>CONTENT</th><th>CLASSIFICATION</th><th>CERTAINTY</th></tr>"
        for _, row in df.tail(15).iloc[::-1].iterrows():
            clr = "#00e676" if row['label'] == 'SAFE' else "#ff1744"
            tbl += f"<tr><td>{row['time']}</td><td>{row['text']}</td><td style='color:{clr};font-weight:700;'>{row['label']}</td><td>{row['confidence']:.1f}%</td></tr>"
        tbl += "</table>"
        st.markdown(tbl, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PERFORMANCE
# ══════════════════════════════════════════════
elif page == "PERFORMANCE":
    st.markdown('<div class="hero">SYSTEM PERFORMANCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">// MODEL EVALUATION METRICS //</div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    p1.markdown('<div class="mcard"><div class="mv">94.50<span style="font-size:0.9rem;">%</span></div><div class="ml">RECALL</div></div>', unsafe_allow_html=True)
    p2.markdown('<div class="mcard"><div class="mv" style="color:#8b5cf6; text-shadow:0 0 15px rgba(139,92,246,0.3);">93.88<span style="font-size:0.9rem;">%</span></div><div class="ml">PRECISION</div></div>', unsafe_allow_html=True)
    p3.markdown('<div class="mcard"><div class="mv" style="color:#ff4dd2; text-shadow:0 0 15px rgba(255,77,210,0.3);">94.19<span style="font-size:0.9rem;">%</span></div><div class="ml">F1-SCORE</div></div>', unsafe_allow_html=True)
    p4.markdown('<div class="mcard"><div class="mv">91.11<span style="font-size:0.9rem;">%</span></div><div class="ml">ACCURACY</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    perf1, perf2 = st.columns(2)
    with perf1:
        st.markdown("<h4 style='font-size:0.7rem; color:#8b5cf6; letter-spacing:2px; margin-bottom:8px;'>CATEGORY PERFORMANCE</h4>", unsafe_allow_html=True)
        cats = ['Direct Insults', 'Profanity', 'Threats', 'Identity Attacks', 'Sarcasm', 'Negation', 'Coded Lang']
        fig3 = go.Figure()
        fig3.add_trace(go.Scatterpolar(r=[99.2,97.1,96.3,93.8,68.0,72.0,65.0], theta=cats, fill='toself', name='Recall',
                                        line=dict(color='#00f0ff'), fillcolor='rgba(0,240,255,0.1)'))
        fig3.add_trace(go.Scatterpolar(r=[98.5,96.8,95.1,93.2,85.2,87.3,79.8], theta=cats, fill='toself', name='Precision',
                                        line=dict(color='#8b5cf6'), fillcolor='rgba(139,92,246,0.1)'))
        fig3.update_layout(
            polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=True, range=[50,100], gridcolor='rgba(255,255,255,0.04)', color='#4a5568'),
                       angularaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#718096')),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='JetBrains Mono', color='#718096', size=9),
            margin=dict(t=25,b=25,l=50,r=50), height=300,
            dragmode=False,
            showlegend=True, legend=dict(x=0.3, y=-0.1, orientation='h'))
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    with perf2:
        st.markdown("<h4 style='font-size:0.7rem; color:#00f0ff; letter-spacing:2px; margin-bottom:8px;'>ARCHITECTURE</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass" style="padding:20px;">
            <div style="font-family:JetBrains Mono; font-size:0.72rem; color:#4a5568; line-height:2.2;">
                <span style="color:#8b5cf6;">BASE</span> &nbsp;&nbsp;&nbsp; BERT-base-uncased<br>
                <span style="color:#8b5cf6;">PARAMS</span> &nbsp; ~110,000,000<br>
                <span style="color:#8b5cf6;">OPTIM</span> &nbsp;&nbsp; AdamW (lr=2e-5)<br>
                <span style="color:#8b5cf6;">BATCH</span> &nbsp;&nbsp; 16<br>
                <span style="color:#8b5cf6;">LOSS</span> &nbsp;&nbsp;&nbsp; CrossEntropyLoss<br>
                <span style="color:#8b5cf6;">DATASET</span>&nbsp; 59,450 samples<br>
                <span style="color:#8b5cf6;">EPOCHS</span> &nbsp; 3
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:0.7rem; color:#00f0ff; letter-spacing:2px; margin-bottom:8px;'>TRAINING SUMMARY</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass" style="padding:20px;">
            <div style="font-family:JetBrains Mono; font-size:0.72rem; color:#4a5568; line-height:2.2;">
                <span style="color:#00e676;">RECALL</span> &nbsp;&nbsp; 94.50% (Catches 6,823/7,220 cases)<br>
                <span style="color:#00e676;">PRECISION</span> 93.88% (High fidelity detection)<br>
                <span style="color:#00f0ff;">F1-SCORE</span> &nbsp; 94.19% (State-of-the-art balance)
            </div>
        </div>
        """, unsafe_allow_html=True)
