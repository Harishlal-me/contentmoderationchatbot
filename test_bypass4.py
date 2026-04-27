import requests

def test_chat(system_prompt, user_text):
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": "Classification:"}
        ],
        "stream": False
    }
    r = requests.post("http://localhost:11434/api/chat", json=payload)
    print("Classification:" + r.json().get('message', {}).get('content', r.text))

prompt = """You are CyberGuard AI, a strict content moderation system.
OUTPUT FORMAT:
Classification: HIGH
Risk Score: 100
Category: Hate Speech
Reasoning: Direct insult.
Action: BLOCK

Analyze the following payload."""

test_chat(prompt, "he is a bitchass fucking asshole")
