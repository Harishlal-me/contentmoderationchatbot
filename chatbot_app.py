import streamlit as st
import warnings
from src.chat_controller import ChatController
import time

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="CyberGuard AI Platform",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── PREMIUM SAAS UI CSS INJECTION ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* Main Body Override */
.stApp {
    background-color: #0E1117;
    color: #FAFAFA;
    font-family: 'Inter', sans-serif;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #161B22 !important;
    border-right: 1px solid #30363D;
}
[data-testid="stSidebar"] .stButton > button {
    background-color: transparent !important;
    border: none !important;
    color: #E6EDF3 !important;
    font-weight: 500;
    text-align: left;
    width: 100%;
    padding: 12px 16px;
    border-radius: 8px;
    transition: all 0.2s ease;
    justify-content: flex-start;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #21262D !important;
}

/* Header Adjustments */
h1 {
    font-weight: 600 !important;
    font-size: 2rem !important;
    letter-spacing: -0.5px;
    color: #FFFFFF;
    border-bottom: 1px solid #30363D;
    padding-bottom: 15px;
    margin-bottom: 30px;
}

/* Chat Input Styling */
.stChatInputContainer {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
}
.stChatInput textarea {
    color: #FAFAFA !important;
}

/* Chat Bubbles */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 10px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #161B22 !important;
    border-radius: 12px;
    padding: 16px 20px !important;
    border: 1px solid #30363D;
    margin: 15px 0;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    padding: 16px 5px !important;
}

/* Diagnostic Expander */
.st-emotion-cache-p5msec {
    background-color: transparent;
    border: 1px solid #30363D;
    border-radius: 8px;
}
.diag-panel {
    background: #161B22; border-radius: 8px; padding: 12px; margin-top: 5px; border: 1px solid #30363D;
}
.safe-text { color: #3FB950; font-weight: 600; font-size: 0.9rem; letter-spacing: 0.5px; }
.threat-text { color: #F85149; font-weight: 600; font-size: 0.9rem; letter-spacing: 0.5px; }

/* In-Chat Action Buttons */
.rewrite-btn-container .stButton > button {
    background-color: #21262D !important;
    border: 1px solid #30363D !important;
    color: #A5D6FF !important;
    font-size: 0.8rem;
    padding: 2px 10px;
    border-radius: 6px;
    margin-top: 5px;
}
.rewrite-btn-container .stButton > button:hover {
    background-color: #30363D !important;
    color: #FFFFFF !important;
}

</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INITIALIZATION ──
if "controller" not in st.session_state:
    st.session_state.controller = ChatController()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you analyze, moderate, or assess digital interactions today?"}
    ]

# Action hooks
def clear_history():
    st.session_state.messages = [st.session_state.messages[0]]

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'><h2 style='border-bottom:none; margin:0;'>🛡️ CyberGuard</h2></div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background:#21262D; border:1px solid #30363D; padding:8px 12px; border-radius:6px; display:flex; align-items:center; gap:8px; margin-bottom:30px;">
            <div style="width:8px;height:8px;background:#3FB950;border-radius:50%;"></div>
            <span style="color:#8B949E;font-size:0.8rem;font-weight:500;">Connected to Local Network</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='color:#8B949E; font-size:0.8rem; font-weight:600; letter-spacing:1px; margin-bottom:10px;'>MODULES</div>", unsafe_allow_html=True)
    
    if st.button("📝 Generate Quiz"):
        st.session_state.trigger_cmd = "QUIZ"
    if st.button("📊 Start Assessment"):
        st.session_state.trigger_cmd = "ASSESS"
                
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History"):
        clear_history()
        st.rerun()

# ── MAIN UI ──
st.title("Content Moderation Console")

# Render existing chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Diagnostic details
        if "bert_info" in msg:
            info = msg["bert_info"]
            is_threat = info["is_threat"]
            
            c_tag = "threat" if is_threat else "safe"
            c_label = "⚠️ Cyberbullying Detected" if is_threat else "✅ Safe Content"
            c_color = "#F85149" if is_threat else "#3FB950"
            
            with st.expander("Model Diagnostics & Reasoning"):
                st.markdown(f"""
                <div class="diag-panel">
                    <div class="{c_tag}-text">{c_label}</div>
                    <div style="margin-top:4px; font-size:0.8rem; color:#8B949E;">BERT Threat Confidence: {info['confidence']*100:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
                



# ── STREAMING GENERATORS PIPELINE ──

# Handle programmatic triggers from sidebar / buttons
if "trigger_cmd" in st.session_state:
    cmd_val = st.session_state.trigger_cmd
    del st.session_state.trigger_cmd
    
    with st.chat_message("assistant"):
        if isinstance(cmd_val, tuple) and cmd_val[0] == "REWRITE":
            st.markdown(f"**Generating safe alternatives for:** _{cmd_val[1]}_\n")
            with st.spinner("Analyzing semantics..."):
                gen = st.session_state.controller.process_command(cmd_val[0], cmd_val[1], st.session_state.messages)
                final_output = st.write_stream(gen)
        else:
            with st.spinner("Generating module..."):
                gen = st.session_state.controller.process_command(cmd_val, "", st.session_state.messages)
                final_output = st.write_stream(gen)
        
        st.session_state.messages.append({"role": "assistant", "content": final_output})
        st.rerun()

# Handle direct user input
elif prompt := st.chat_input("Message CyberGuard AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing message..."):
            pipeline_result = st.session_state.controller.process_message(prompt, st.session_state.messages)
            
            # Stream the generator returned by LLM
            final_output = st.write_stream(pipeline_result["response_generator"])
            
            b_info = pipeline_result["bert"]
            is_threat = b_info["is_threat"]
            
            c_tag = "threat" if is_threat else "safe"
            c_label = "⚠️ Cyberbullying Detected" if is_threat else "✅ Safe Content"
            
            with st.expander("Model Diagnostics & Reasoning"):
                st.markdown(f"""
                <div class="diag-panel">
                    <div class="{c_tag}-text">{c_label}</div>
                    <div style="margin-top:4px; font-size:0.8rem; color:#8B949E;">BERT Threat Confidence: {b_info['confidence']*100:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Persist to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_output,
                "bert_info": b_info
            })
            st.rerun()
