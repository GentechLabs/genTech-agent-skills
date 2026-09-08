"""
Hermes Web Bridge Server — Template
Copy this and customize for your use case.

Required env vars:
  HERMES_PROFILE — Hermes profile to use (default: gentech)
  BRIDGE_PORT — Port to listen on (default: 8765)
"""
import os
import sys
import secrets
import asyncio
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# ─── Config ─────────────────────────────────────────────────────────
PORT = int(os.environ.get("BRIDGE_PORT", "8765"))
PROFILE = os.environ.get("HERMES_PROFILE", "gentech")

app = FastAPI(title="Hermes Bridge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict = {}


async def ask_hermes(message: str, session_id: str = None) -> dict:
    """Send a message to Hermes via CLI and get the response."""
    cmd = ["hermes", "-p", PROFILE, "chat", "-q", message, "-Q"]
    if session_id:
        cmd.extend(["--resume", session_id])

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "HERMES_YOLO_MODE": "1"},
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        output = stdout.decode().strip()

        new_session_id = session_id
        response_text = output
        if output.startswith("session_id:"):
            lines = output.split("\n", 1)
            new_session_id = lines[0].replace("session_id:", "").strip()
            response_text = lines[1].strip() if len(lines) > 1 else ""

        return {"response": response_text or "(no response)", "session_id": new_session_id, "ok": True}
    except asyncio.TimeoutError:
        return {"response": "Timed out.", "ok": False, "session_id": session_id}
    except Exception as e:
        return {"response": f"Error: {e}", "ok": False, "session_id": session_id}


@app.get("/", response_class=HTMLResponse)
async def index():
    html = Path(__file__).parent / "index.html"
    return HTMLResponse(html.read_text() if html.exists() else "<h1>No UI</h1>")


@app.post("/api/session")
async def create_session(request: Request):
    body = await request.json()
    label = body.get("label", "user")
    token = secrets.token_urlsafe(32)
    result = await ask_hermes(f"Greet {label} briefly — 1-2 sentences.")
    sessions[token] = {"hermes_session": result.get("session_id"), "label": label}
    return {"token": token, "greeting": result.get("response", "Hey!"), "status": "connected"}


@app.post("/api/chat")
async def chat(request: Request):
    auth = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if auth not in sessions:
        raise HTTPException(401, "Invalid session")
    body = await request.json()
    message = body.get("message", "").strip()
    if not message:
        raise HTTPException(400, "Empty message")
    sess = sessions[auth]
    result = await ask_hermes(message, sess.get("hermes_session"))
    if result.get("session_id"):
        sess["hermes_session"] = result["session_id"]
    return {"response": result.get("response", "No response"), "ok": result.get("ok", False)}


@app.get("/api/health")
async def health():
    return {"status": "ok", "profile": PROFILE, "sessions": len(sessions), "time": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
