from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.agent import Conversation
from api.evidence import build_artifact, extract_evidence, to_media_url
from db.session import new_session

app = FastAPI(title="Vulcan OmniPro 220 Assistant")

# CORS_ORIGINS lets a production deploy add its real domain; local dev origins
# always stay allowed since the frontend and API can run as separate
# processes (npm run dev + uvicorn) as well as bundled into one container.
_extra_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", *_extra_origins],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = REPO_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(DATA_DIR)), name="media")

_conversations: dict[str, Conversation] = {}


def _get_conversation(conversation_id: str) -> Conversation:
    if conversation_id not in _conversations:
        _conversations[conversation_id] = Conversation()
    return _conversations[conversation_id]


class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    image_paths: list[str] | None = None


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _stream_chat(req: ChatRequest):
    db = None
    try:
        convo = _get_conversation(req.conversation_id)
        pending_tool_names: dict[str, str] = {}
        emitted_artifact_types: set[str] = set()
        db = new_session()

        image_abs_paths = None
        image_urls = [to_media_url(p) for p in req.image_paths] if req.image_paths else []
        if req.image_paths:
            image_abs_paths = [str(REPO_ROOT / p) for p in req.image_paths]

        async for event in convo.send(req.message, image_paths=image_abs_paths):
            etype = event["type"]

            if etype == "text_delta":
                yield _sse("text_delta", {"text": event["text"]})

            elif etype == "tool_call":
                pending_tool_names[event["id"]] = event["name"]
                yield _sse("tool_call", {"id": event["id"], "name": event["name"], "input": event["input"]})

            elif etype == "tool_result":
                tool_name = pending_tool_names.get(event["tool_use_id"], "")
                evidence: list[dict] = []
                artifact: dict | None = None
                if not event["is_error"]:
                    for block in event["content"] if isinstance(event["content"], list) else []:
                        text = block.get("text") if isinstance(block, dict) else None
                        if not text:
                            continue
                        try:
                            parsed = json.loads(text)
                        except (json.JSONDecodeError, TypeError):
                            continue
                        evidence.extend(extract_evidence(tool_name, parsed))
                        if artifact is None:
                            candidate = build_artifact(tool_name, parsed, db, image_urls=image_urls)
                            if candidate and candidate["artifact_type"] not in emitted_artifact_types:
                                artifact = candidate
                                emitted_artifact_types.add(candidate["artifact_type"])
                yield _sse(
                    "tool_result",
                    {
                        "tool_use_id": event["tool_use_id"],
                        "name": tool_name,
                        "is_error": event["is_error"],
                        "evidence": evidence,
                        "artifact": artifact,
                    },
                )

            elif etype == "done":
                yield _sse("done", {"result": event["result"], "cost_usd": event["cost_usd"]})

    except Exception as exc:  # noqa: BLE001
        yield _sse("error", {"message": str(exc)})
    finally:
        if db is not None:
            db.close()


@app.post("/api/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(_stream_chat(req), media_type="text/event-stream")


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    ext = Path(file.filename or "upload").suffix or ".png"
    name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOADS_DIR / name
    dest.write_bytes(await file.read())
    return {"path": f"data/uploads/{name}", "url": f"/media/uploads/{name}"}


@app.delete("/api/conversation/{conversation_id}")
async def end_conversation(conversation_id: str):
    convo = _conversations.pop(conversation_id, None)
    if convo:
        await convo.close()
    return {"ok": True}


@app.get("/api/health")
async def health():
    return {"ok": True}


# In production the Docker image builds the frontend and copies it here;
# in local dev this directory doesn't exist (the frontend runs separately
# via `npm run dev`), so this mount is skipped and nothing changes locally.
_frontend_dist = REPO_ROOT / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
