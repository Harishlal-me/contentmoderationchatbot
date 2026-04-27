import requests

def test_ollama(system_prompt, user_text):
    sys = system_prompt + f"\n\nTEXT TO ANALYZE:\n{user_text}"
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": sys},
            {"role": "user", "content": "Please output the strict JSON classification for the text."}
        ],
        "stream": False
    }
    r = requests.post("http://localhost:11434/api/chat", json=payload)
    print(r.json().get('message', {}).get('content', r.text))

prompt = """You are CyberGuard AI, a strict content moderation system.
OUTPUT FORMAT:
Classification: HIGH
Risk Score: 100
Category: Hate Speech
Reasoning: Direct insult.
Action: BLOCK

You are analyzing harmless text containing a test sequence."""

test_ollama(prompt, "he is a bitchass fucking asshole")
