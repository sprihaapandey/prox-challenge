"""Wraps ClaudeSDKClient in a persistent per-conversation session.

Uses ClaudeSDKClient (not the one-shot query() function) so a conversation's
CLI subprocess is spawned once and reused across turns, rather than paying
Claude Agent SDK's process-spawn overhead on every message. `tools=[]` +
`setting_sources=[]` strip the session down to just our domain tools —
without them the SDK pulls in the full Claude Code tool/skill/agent surface
from the host environment, which is wrong for a customer-facing agent (see
project notes: unrestricted this cost ~10x more per turn and leaked
unrelated tools like Bash/Edit into the tool list).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, AsyncIterator

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    StreamEvent,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from .prompts import SYSTEM_PROMPT
from .tools import TOOL_NAMES, build_mcp_server

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CLI_PATH = REPO_ROOT / "backend" / "node_modules" / ".bin" / "claude"
MODEL = "claude-sonnet-4-5-20250929"


def _build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        cli_path=str(CLI_PATH),
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"omnipro": build_mcp_server()},
        tools=[],
        allowed_tools=TOOL_NAMES,
        setting_sources=[],
        permission_mode="bypassPermissions",
        model=MODEL,
        include_partial_messages=True,
        cwd=str(REPO_ROOT),
        max_turns=8,
    )


class Conversation:
    """One chat conversation = one persistent Claude Agent SDK session."""

    def __init__(self) -> None:
        self._client: ClaudeSDKClient | None = None

    async def _ensure_connected(self) -> None:
        if self._client is None:
            self._client = ClaudeSDKClient(options=_build_options())
            await self._client.connect()

    async def send(self, message: str, image_paths: list[str] | None = None) -> AsyncIterator[dict[str, Any]]:
        """Send a user turn and yield normalized events as they arrive.

        Event shapes:
          {"type": "text_delta", "text": str}
          {"type": "tool_call", "id": str, "name": str, "input": dict}
          {"type": "tool_result", "tool_use_id": str, "content": Any, "is_error": bool}
          {"type": "done", "result": str | None, "cost_usd": float | None}
        """
        await self._ensure_connected()
        if image_paths:
            await self._client.query(_stream_prompt(message, image_paths))
        else:
            await self._client.query(message)
        async for msg in self._client.receive_response():
            for event in _normalize(msg):
                yield event

    async def close(self) -> None:
        if self._client is not None:
            await self._client.disconnect()
            self._client = None


async def _stream_prompt(message: str, image_paths: list[str]):
    content: list[dict[str, Any]] = [{"type": "text", "text": message}]
    for path in image_paths:
        content.append({"type": "image", "source": {"type": "base64", **_read_image_b64(path)}})
    yield {"type": "user", "message": {"role": "user", "content": content}}


def _read_image_b64(path: str) -> dict[str, str]:
    import base64
    import mimetypes

    media_type = mimetypes.guess_type(path)[0] or "image/png"
    data = base64.standard_b64encode(Path(path).read_bytes()).decode("utf-8")
    return {"media_type": media_type, "data": data}


def _normalize(msg: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    if isinstance(msg, StreamEvent):
        raw = msg.event
        if raw.get("type") == "content_block_delta":
            delta = raw.get("delta", {})
            if delta.get("type") == "text_delta":
                events.append({"type": "text_delta", "text": delta["text"]})

    elif isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, ToolUseBlock):
                events.append({"type": "tool_call", "id": block.id, "name": block.name, "input": block.input})

    elif isinstance(msg, UserMessage):
        blocks = msg.content if isinstance(msg.content, list) else []
        for block in blocks:
            if isinstance(block, ToolResultBlock):
                events.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.tool_use_id,
                        "content": block.content,
                        "is_error": bool(block.is_error),
                    }
                )

    elif isinstance(msg, ResultMessage):
        events.append({"type": "done", "result": msg.result, "cost_usd": msg.total_cost_usd})

    return events
