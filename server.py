"""
Islamic Guidance Assistant - FastAPI Backend
Serves the custom chat UI and handles WebSocket streaming.
"""
import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from agents import Runner

from agent_core import agent

app = FastAPI(title="Islamic Guidance Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, assets)
PUBLIC_DIR = Path(__file__).parent / "public"
if PUBLIC_DIR.exists():
    app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

# Session memory store: {session_id: [(q, a), ...]}
session_memory: dict[str, list] = {}
MAX_MEMORY = 5


@app.get("/")
async def serve_index():
    """Serve the main chat UI."""
    index_path = PUBLIC_DIR / "index.html"
    if not index_path.exists():
        return PlainTextResponse("Error: index.html is missing from the deployment.", status_code=500)
    return FileResponse(str(index_path))

@app.post("/chat")
async def chat_endpoint(request: Request):
    """HTTP POST endpoint for chat (Fallback for environments without WebSockets)."""
    try:
        data = await request.json()
        query = data.get("message", "").strip()
        session_id = data.get("session_id", "default")

        if not query:
            return {"type": "error", "message": "Empty message"}

        if session_id not in session_memory:
            session_memory[session_id] = []

        memory = session_memory[session_id]

        # Build context prompt from memory
        context_prompt = ""
        if memory:
            context_prompt = "Previous questions and answers:\n"
            for i, (q, a) in enumerate(memory[-MAX_MEMORY:], 1):
                context_prompt += f"\nQ{i}: {q}\nA{i}: {a}\n"

        contextual_query = context_prompt + f"\nNow answer this: {query}"

        # Run agent
        result = await Runner.run(agent, input=contextual_query)
        answer = result.final_output

        # Store in memory
        memory.append((query, answer))
        session_memory[session_id] = memory

        return {
            "type": "response",
            "message": answer
        }

    except Exception as e:
        return {
            "type": "error",
            "message": str(e)
        }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in session_memory:
        session_memory[session_id] = []

    try:
        while True:
            # Receive user message
            data = await websocket.receive_text()
            msg = json.loads(data)
            query = msg.get("message", "").strip()

            if not query:
                continue

            memory = session_memory[session_id]

            # Build context prompt from memory
            context_prompt = ""
            if memory:
                context_prompt = "Previous questions and answers:\n"
                for i, (q, a) in enumerate(memory[-MAX_MEMORY:], 1):
                    context_prompt += f"\nQ{i}: {q}\nA{i}: {a}\n"

            contextual_query = context_prompt + f"\nNow answer this: {query}"

            # Send "thinking" status
            await websocket.send_text(json.dumps({
                "type": "thinking",
                "message": "Searching Quran and sources..."
            }))

            try:
                # Run agent
                result = await Runner.run(agent, input=contextual_query)
                answer = result.final_output

                # Store in memory
                memory.append((query, answer))
                session_memory[session_id] = memory

                # Send complete response
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "message": answer
                }))

            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"An error occurred: {str(e)}"
                }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)
