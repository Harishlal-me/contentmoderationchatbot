import urllib.request
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.dumps({
    "prompt": "analyse this text \"he is a gay\"",
    "history": []
}).encode("utf-8")

req = urllib.request.Request("http://127.0.0.1:8000/api/chat", data=data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    print(response.read().decode('utf-8'))
