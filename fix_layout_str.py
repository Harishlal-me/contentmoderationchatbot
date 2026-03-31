import codecs

file_path = "d:/cyberbullying-detection-main/streamlit_app.py"

with codecs.open(file_path, 'r', 'utf-8') as f:
    text = f.read()

# 1. DELETE REACT PANEL
start_target = "        st.markdown(\"<div style='height:40px'></div>\", unsafe_allow_html=True)\n        st.markdown(\"<h4 style='font-size:0.7rem; color:#8b5cf6; letter-spacing:2px; margin-bottom:8px;'>LIVE THREAT SCORE PANEL</h4>\""
end_target = "components.html(react_tailwind_panel, height=520)\n"

s_idx = text.find(start_target)
e_idx = text.find(end_target)

if s_idx != -1 and e_idx != -1:
    text = text[:s_idx] + "\n        pass\n" + text[e_idx + len(end_target):]
    print("Deleted Live Threat Score Panel.")
else:
    print("Could not find boundaries for panel.")
    
# 2. MOVE QUICK TEST EXAMPLES
target_old = """        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:0.85rem; color:#8b5cf6; letter-spacing:2px; margin-bottom:12px;'>QUICK TEST EXAMPLES</h4>", unsafe_allow_html=True)
        
        examples_html = \"\"\"
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
        \"\"\"
        st.markdown(examples_html, unsafe_allow_html=True)"""

target_new = """    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h4 style='text-align:center; font-size:0.85rem; color:#8b5cf6; letter-spacing:2px; margin-bottom:12px;'>QUICK TEST EXAMPLES</h4>", unsafe_allow_html=True)
        
        examples_html = \"\"\"
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
        \"\"\"
        st.markdown(examples_html, unsafe_allow_html=True)"""

if target_old in text:
    text = text.replace(target_old, target_new)
    print("Replaced Examples.")
else:
    print("Could not find Target Old.")

with codecs.open(file_path, 'w', 'utf-8') as f:
    f.write(text)
    
print("Rewrite Complete.")
