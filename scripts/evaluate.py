#!/usr/bin/env python3
"""Runs the evaluation dataset (tests/eval/dataset.py) against the live agent
and writes a report. Automated checks cover what's cheap and reliable (was
the right tool called, does an expected substring appear, is an expected
page cited, did it ask a clarifying question); everything else -- the
"accuracy", "hallucination rate" style metrics from the plan that require
judgment -- is left for a human to grade from the saved full transcript.

Usage:
    backend/.venv/bin/python scripts/evaluate.py                # full run
    backend/.venv/bin/python scripts/evaluate.py --category sf  # id-prefix filter
    backend/.venv/bin/python scripts/evaluate.py --limit 5       # smoke test
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))
sys.path.insert(0, str(REPO_ROOT / "tests"))

from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")

from agent.agent import Conversation  # noqa: E402
from eval.dataset import DATASET, EvalQuestion  # noqa: E402

CONCURRENCY = 2
PER_QUESTION_TIMEOUT_S = 90  # a single hung CLI subprocess must not block the whole suite forever
OUT_DIR = REPO_ROOT / "tests" / "eval" / "results"


async def run_question(q: EvalQuestion, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        convo = Conversation()
        text = ""
        tool_calls: list[dict] = []
        error = None
        started = time.monotonic()
        try:
            async with asyncio.timeout(PER_QUESTION_TIMEOUT_S):
                async for event in convo.send(q.question):
                    if event["type"] == "text_delta":
                        text += event["text"]
                    elif event["type"] == "tool_call":
                        tool_calls.append({"name": event["name"].rsplit("__", 1)[-1], "input": event["input"]})
        except TimeoutError:
            error = f"timed out after {PER_QUESTION_TIMEOUT_S}s"
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
        finally:
            try:
                async with asyncio.timeout(10):
                    await convo.close()
            except Exception:  # noqa: BLE001
                pass  # best-effort cleanup; a hung subprocess shouldn't block the report either
        elapsed = time.monotonic() - started

    checks = grade(q, text, tool_calls)
    status = "ERROR" if error else ("ok" if all(v is not False for v in checks.values()) else "check-failed")
    print(f"[{status:12s}] {q.id:8s} {elapsed:5.1f}s  {q.question[:60]}", flush=True)
    return {
        "id": q.id,
        "category": q.category,
        "question": q.question,
        "answer": text,
        "tool_calls": tool_calls,
        "error": error,
        "elapsed_s": round(elapsed, 1),
        "checks": checks,
        "notes": q.notes,
    }


def grade(q: EvalQuestion, text: str, tool_calls: list[dict]) -> dict:
    checks: dict[str, bool | None] = {}
    text_lower = text.lower()
    called_names = {tc["name"] for tc in tool_calls}

    if q.expected_tool_names is not None:
        checks["expected_tool_called"] = any(t in called_names for t in q.expected_tool_names)
    if q.expected_answer_contains is not None:
        checks["expected_substrings_present"] = all(s.lower() in text_lower for s in q.expected_answer_contains)
    if q.expected_source_pages is not None:
        checks["expected_source_page_cited"] = any(str(p) in text for p in q.expected_source_pages)
    if q.expect_clarification:
        checks["asked_clarifying_question"] = "?" in text

    return checks


def summarize(results: list[dict]) -> dict:
    by_category: dict[str, dict] = {}
    for r in results:
        cat = r["category"]
        by_category.setdefault(cat, {"total": 0, "checks_passed": 0, "checks_total": 0, "errors": 0})
        by_category[cat]["total"] += 1
        if r["error"]:
            by_category[cat]["errors"] += 1
        for passed in r["checks"].values():
            if passed is None:
                continue
            by_category[cat]["checks_total"] += 1
            if passed:
                by_category[cat]["checks_passed"] += 1
    return by_category


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", help="only run questions whose id starts with this prefix, e.g. 'sf'")
    parser.add_argument("--limit", type=int, help="only run the first N matching questions")
    args = parser.parse_args()

    questions = DATASET
    if args.category:
        questions = [q for q in questions if q.id.startswith(args.category)]
    if args.limit:
        questions = questions[: args.limit]

    print(f"Running {len(questions)} evaluation questions (concurrency={CONCURRENCY})...")
    semaphore = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(*[run_question(q, semaphore) for q in questions])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"run_{int(time.time())}.json"
    out_path.write_text(json.dumps(results, indent=2))

    summary = summarize(results)
    print("\n=== Summary by category ===")
    total_passed = total_checked = 0
    for cat, s in sorted(summary.items()):
        rate = f"{s['checks_passed']}/{s['checks_total']}" if s["checks_total"] else "n/a (manual review)"
        print(f"{cat:16s} {s['total']:3d} questions  automated checks: {rate}  errors: {s['errors']}")
        total_passed += s["checks_passed"]
        total_checked += s["checks_total"]

    print(f"\nOverall automated check pass rate: {total_passed}/{total_checked}")
    print(f"Full transcripts written to {out_path}")

    failures = [r for r in results if r["error"] or any(v is False for v in r["checks"].values())]
    if failures:
        print(f"\n{len(failures)} question(s) need review:")
        for r in failures:
            failed_checks = [k for k, v in r["checks"].items() if v is False]
            print(f"  [{r['id']}] {r['question'][:70]}")
            if r["error"]:
                print(f"      ERROR: {r['error']}")
            if failed_checks:
                print(f"      failed checks: {failed_checks}")


if __name__ == "__main__":
    asyncio.run(main())
