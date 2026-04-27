import os
import sys
import json
import asyncio
import io
from datetime import datetime

# Force UTF-8 encoding locally to avoid charmap codec crashes 
# if BERT or other modules print unicode symbols (e.g. checkmarks)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from src.chat_controller import ChatController

app = FastAPI(title="CyberGuard AI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

controller = ChatController()

# ── In-memory session store ──────────────────────────────────
# Keyed by user_id (frontend passes "default" for single-user mode)
_SESSION_STORE: dict[str, list[dict]] = {}

def _generate_summary(risk_score: int) -> str:
    if risk_score >= 70:
        return "Direct harmful or abusive language"
    elif risk_score >= 40:
        return "Potentially negative or sarcastic tone"
    else:
        return "Safe and non-harmful"

def _get_status_label(risk_score: int) -> str:
    if risk_score >= 70:
        return "UNSAFE"
    elif risk_score >= 40:
        return "WARNING"
    else:
        return "SAFE"

def _analyze_performance(scores: list[int]) -> str:
    if len(scores) < 2:
        return "Not enough data yet — send more messages to see trends."
    if scores[-1] > scores[0] + 10:
        return "Behavior is worsening — risk is increasing over time."
    elif scores[-1] < scores[0] - 10:
        return "Behavior is improving — risk is decreasing over time."
    else:
        return "Behavior is stable — risk score is consistent."

def _generate_suggestion(scores: list[int]) -> str:
    if not scores:
        return ""
    avg = sum(scores) / len(scores)
    if avg > 70:
        return "Try avoiding aggressive or insulting language."
    elif avg > 40:
        return "Be mindful of tone — some messages may sound negative."
    else:
        return "Your communication is clear and respectful. Keep it up!"

class Message(BaseModel):
    role: str
    content: str
    bert_info: Optional[dict] = None

class ChatRequest(BaseModel):
    prompt: str
    history: List[Message]
    user_id: str = "default"

class CommandRequest(BaseModel):
    cmd: str
    metadata: str
    history: List[Message]

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    history_dicts = []
    for m in req.history:
        info = m.bert_info or {}
        history_dicts.append({
            "role": m.role,
            "content": m.content,
            "risk_score": info.get("risk_score", 0),
            "is_threat": info.get("is_threat", False)
        })

    user_id = req.user_id
    result = controller.process_message(req.prompt, history_dicts)

    # Track ALL analyzed messages in the session store
    bert = result.bert
    risk_score = bert.get("risk_score", 0)
    # Track if BERT ran (is_threat is set, even if False = explicit safe result)
    if "is_threat" in bert:
        entry = {
            "text": req.prompt[:120],
            "risk_score": risk_score,
            "status": _get_status_label(risk_score),
            "summary": _generate_summary(risk_score),
            "confidence": round(bert.get("confidence", 0) * 100, 1),
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        _SESSION_STORE.setdefault(user_id, []).append(entry)

    async def text_generator():
        yield json.dumps(result.bert) + "\n|||\n"
        gen = result.response_generator
        for chunk in gen:
            await asyncio.sleep(0.01)
            yield chunk

    return StreamingResponse(text_generator(), media_type="text/plain")


@app.post("/api/command")
async def command_endpoint(req: CommandRequest):
    history_dicts = []
    for m in req.history:
        info = m.bert_info or {}
        history_dicts.append({
            "role": m.role,
            "content": m.content,
            "risk_score": info.get("risk_score", 0),
            "is_threat": info.get("is_threat", False)
        })
        
    gen = controller.process_command(req.cmd, req.metadata, history_dicts)
    
    async def text_generator():
        yield "{}\n|||\n"
        for chunk in gen:
            await asyncio.sleep(0.01)
            yield chunk
            
    return StreamingResponse(text_generator(), media_type="text/plain")


@app.get("/api/session/{user_id}")
def get_session(user_id: str):
    """Return live session stats + performance analysis for the dashboard."""
    history = _SESSION_STORE.get(user_id, [])
    total   = len(history)
    toxic   = sum(1 for m in history if m["risk_score"] > 60)
    avg     = round(sum(m["risk_score"] for m in history) / total, 1) if total else 0.0
    scores  = [m["risk_score"] for m in history]
    return {
        "history": history,
        "stats": {
            "total":   total,
            "toxic":   toxic,
            "avg":     avg,
        },
        "insight":    _analyze_performance(scores),
        "suggestion": _generate_suggestion(scores),
    }


@app.delete("/api/session/{user_id}")
def reset_session(user_id: str):
    """Clear session data (e.g. after 'New Chat')."""
    _SESSION_STORE.pop(user_id, None)
    return {"ok": True}
