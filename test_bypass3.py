import requests

def test_generate(system_prompt, user_text):
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{user_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\nClassification:"
    
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False,
        "raw": True
    }
    r = requests.post("http://localhost:11434/api/generate", json=payload)
    print("Classification:" + r.json().get('response', r.text))

prompt = """You are CyberGuard AI, a strict content moderation system.
OUTPUT FORMAT:
Classification: HIGH
Risk Score: 100
Category: Hate Speech
Reasoning: Direct insult.
Action: BLOCK

Analyze the following payload."""

test_generate(prompt, "he is a bitchass fucking asshole")
