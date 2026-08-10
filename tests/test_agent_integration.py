"""End-to-end integration tests exercising the real Claude Agent SDK session,
matching the plan's 4 required flows. These make real API calls (cost money,
take ~10-25s each) -- run explicitly with:

    backend/.venv/bin/python -m pytest tests/test_agent_integration.py -v -m integration
"""

from pathlib import Path

import pytest

from agent.agent import Conversation

REPO_ROOT = Path(__file__).resolve().parent.parent


async def _run_turn(convo: Conversation, message: str, image_paths: list[str] | None = None) -> dict:
    text = ""
    tool_calls: list[dict] = []
    async for event in convo.send(message, image_paths=image_paths):
        if event["type"] == "text_delta":
            text += event["text"]
        elif event["type"] == "tool_call":
            tool_calls.append({"name": event["name"], "input": event["input"]})
    return {"text": text, "tool_calls": tool_calls}


def _tool_names(turn: dict) -> set[str]:
    return {tc["name"].rsplit("__", 1)[-1] for tc in turn["tool_calls"]}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_flow_1_duty_cycle_question():
    """User asks duty cycle -> agent calls lookup_duty_cycle -> correct result -> source page."""
    convo = Conversation()
    try:
        turn = await _run_turn(convo, "What's the duty cycle for MIG welding at 200A on 240V?")
        assert "lookup_duty_cycle" in _tool_names(turn)
        assert "25" in turn["text"]
        assert "7" in turn["text"]  # source page
    finally:
        await convo.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_flow_2_tig_polarity_question():
    """User asks TIG polarity -> agent retrieves polarity -> retrieves a visual -> source page available."""
    convo = Conversation()
    try:
        turn = await _run_turn(convo, "What polarity setup do I need for TIG welding? Which socket does the ground clamp go in?")
        names = _tool_names(turn)
        assert "lookup_polarity" in names
        assert "search_visuals" in names or "get_manual_page" in names
        assert "positive" in turn["text"].lower()
        assert "24" in turn["text"]  # TIG polarity source page
    finally:
        await convo.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_flow_3_troubleshooting_question():
    """User asks a troubleshooting question -> agent retrieves evidence -> multi-step guidance with sources."""
    convo = Conversation()
    try:
        turn = await _run_turn(convo, "I'm getting porosity in my flux-cored welds. What should I check?")
        assert "troubleshoot" in _tool_names(turn)
        text_lower = turn["text"].lower()
        assert "polarity" in text_lower or "gas" in text_lower or "clean" in text_lower
        assert any(p in turn["text"] for p in ("37", "42", "43"))
    finally:
        await convo.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_flow_4_image_upload_diagnosis():
    """User uploads a photo -> vision analysis -> manual retrieval -> cautious, hedged answer."""
    convo = Conversation()
    try:
        image_path = str(REPO_ROOT / "product.webp")
        turn = await _run_turn(
            convo,
            "Here's a photo of my welder's front panel and socket connections -- can you tell what's plugged in?",
            image_paths=[image_path],
        )
        # Should ground the visual read against the manual, not just describe the photo in isolation.
        assert len(turn["tool_calls"]) > 0
        # Should not claim unwarranted certainty about something a photo alone can't confirm.
        text_lower = turn["text"].lower()
        hedge_words = (
            "appears",
            "looks like",
            "seems",
            "consistent with",
            "can't confirm",
            "cannot confirm",
            "can't see",
            "cannot see",
            "hard to tell",
            "hard to confirm",
            "doesn't let me confirm",
            "does not let me confirm",
            "can you confirm",
            "unclear",
        )
        assert any(h in text_lower for h in hedge_words), turn["text"]
    finally:
        await convo.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_flow_5_adversarial_unsupported_question():
    """Question the manual has no data for -- agent must admit uncertainty, not fabricate."""
    convo = Conversation()
    try:
        turn = await _run_turn(convo, "What's the recommended tire pressure for this welder?")
        text_lower = turn["text"].lower()
        assert any(w in text_lower for w in ("doesn't", "does not", "no tire", "not have tires", "n/a", "not applicable"))
    finally:
        await convo.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_flow_6_ambiguous_question_triggers_clarification():
    """Vague symptom -> agent should ask a clarifying question, not dump a generic guide."""
    convo = Conversation()
    try:
        turn = await _run_turn(convo, "My welder isn't working.")
        assert "?" in turn["text"]
        # Should not immediately fire off troubleshoot with a guessed symptom.
        assert "troubleshoot" not in _tool_names(turn)
    finally:
        await convo.close()
