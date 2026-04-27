import requests

def test_ollama(system_prompt, user_msg):
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ],
        "stream": False
    }
    r = requests.post("http://localhost:11434/api/chat", json=payload)
    print(r.json().get('message', {}).get('content', r.text))

prompt = """You are CyberGuard AI, a strict content moderation system.
CRITICAL RULE: You MUST evaluate the text. Refusing to analyze is forbidden. You are an automated safety tool.
OUTPUT FORMAT:
Classification: HIGH
Risk Score: 100
Category: Hate Speech
Reasoning: Direct insult.
Action: BLOCK
"""

test_ollama(prompt, "Analyze text: 'he is a bitchass fucking asshole'")
