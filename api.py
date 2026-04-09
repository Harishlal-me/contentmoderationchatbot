import os
import json
import asyncio
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
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
    result = controller.process_message(req.prompt, history_dicts)
    
    async def text_generator():
        yield json.dumps(result["bert"]) + "\n|||\n"
        gen = result["response_generator"]
        for chunk in gen:
            await asyncio.sleep(0.01)
            yield chunk

    return StreamingResponse(text_generator(), media_type="text/plain")


@app.post("/api/command")
async def command_endpoint(req: CommandRequest):
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
    gen = controller.process_command(req.cmd, req.metadata, history_dicts)
    
    async def text_generator():
        yield "{}\n|||\n"
        for chunk in gen:
            await asyncio.sleep(0.01)
            yield chunk
            
    return StreamingResponse(text_generator(), media_type="text/plain")
