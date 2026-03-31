import sys

file_path = "d:\\cyberbullying-detection-main\\streamlit_app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove Live Threat Panel from col_in (lines 565-734) -> index 564:734
# Since Python lists are dynamically sized, let's locate the exact lines rather than hardcoded indexes.
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "LIVE THREAT SCORE PANEL" in line:
        start_idx = i - 1 # Include the <div height> above it
    if "components.html(react_tailwind_panel" in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    del lines[start_idx:end_idx+1]
    print(f"Deleted panel from lines {start_idx} to {end_idx}")
else:
    print("Could not find LIVE THREAT SCORE PANEL boundaries.")

content = ''.join(lines)

target_examples = """        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
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

replacement_examples = """    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
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

if target_examples in content:
    content = content.replace(target_examples, replacement_examples)
    print("Replaced target examples successfully.")
else:
    print("Could not find target examples block.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
