import os
import sys
import json
import asyncio
import io

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

class Message(BaseModel):
    role: str
    content: str
    bert_info: Optional[dict] = None

class ChatRequest(BaseModel):
    prompt: str
    history: List[Message]

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
        
    result = controller.process_message(req.prompt, history_dicts)
    
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

# Trigger reload
