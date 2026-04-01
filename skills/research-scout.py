#!/usr/bin/env python3
"""
research-scout skill (no API key required)
Hunts for new information that challenges or updates existing knowledge.
Uses DuckDuckGo (free, no key) for web search and Ollama (local LLM) for
cross-referencing and summarizing findings.

Requirements: pip install duckduckgo-search ollama
Also requires Ollama running locally: https://ollama.com

Usage:
    python skills/research-scout.py
    python skills/research-scout.py --topics "pyicloud updates,iCloud API 2025"
    python skills/research-scout.py --weekly-review
    python skills/research-scout.py --dry-run
    python skills/research-scout.py --model llama3
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MEMORY_DIR = REPO_ROOT / "memory"
LONG_TERM_MEMORY = MEMORY_DIR / "long-term-memory.md"
PROJECT_MEMORY = MEMORY_DIR / "project-memory.md"
README = REPO_ROOT / "README.md"

DEFAULT_MODEL = "mistral"

DEFAULT_TOPICS = [
    "pyicloud python library updates 2025",
    "iCloud Drive API changes Apple 2025",
    "python file organization automation",
    "chromadb updates 2025",
    "sentence transformers embedding models 2025",
]


def load_existing_docs() -> str:
    parts = []
    for path in [README, LONG_TERM_MEMORY, PROJECT_MEMORY]:
        if path.exists():
            parts.append(f"=== {path.name} ===\n{path.read_text()[:2000]}")
    return "\n\n".join(parts)


def ddg_search(query: str, max_results: int = 5) -> list[dict]:
    """Search DuckDuckGo — no API key needed."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        print(f"  [DDG search error] {e}", file=sys.stderr)
        return []


def call_ollama(prompt: str, model: str) -> str:
    try:
        import ollama
        response = ollama.generate(model=model, prompt=prompt)
        return response["response"]
    except Exception as e:
        print(f"  [Ollama error] {e}", file=sys.stderr)
        return ""


def validate_finding(results: list[dict], existing_docs: str, model: str) -> dict:
    """Cross-reference search results against existing docs."""
    if not results:
        return {"is_new": False, "reason": "no results found"}

    results_text = "\n".join(
        f"- {r.get('title', '')}: {r.get('body', '')[:300]} ({r.get('href', '')})"
        for r in results[:3]
    )

    prompt = (
        "Given these web search results:\n"
        f"{results_text}\n\n"
        "And these existing project docs:\n"
        f"{existing_docs[:3000]}\n\n"
        "Is any of this NEW or CONTRADICTORY to the existing docs? "
        'Reply with JSON only: {"is_new": true/false, "reason": "...", '
        '"one_line_summary": "...", "source_url": "..."}'
    )

    response = call_ollama(prompt, model)
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # Fallback: if ollama unavailable, store top result directly
    if results:
        return {
            "is_new": True,
            "reason": "ollama unavailable — stored raw result",
            "one_line_summary": results[0].get("title", "") + " — " + results[0].get("body", "")[:100],
            "source_url": results[0].get("href", ""),
        }
    return {"is_new": False, "reason": "parse error"}


def append_to_new_learnings(finding: dict) -> None:
    text = LONG_TERM_MEMORY.read_text()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    source = finding.get("source_url") or "unknown"
    summary = finding.get("one_line_summary", "").strip()
    entry = f"- [{timestamp}] Source: {source} | Finding: {summary}\n"
    if "## new_learnings" in text:
        text = text.replace("## new_learnings\n", f"## new_learnings\n\n{entry}")
    else:
        text = text.rstrip() + f"\n\n## new_learnings\n\n{entry}"
    LONG_TERM_MEMORY.write_text(text)


def weekly_review(model: str, dry_run: bool = False) -> None:
    text = LONG_TERM_MEMORY.read_text()
    match = re.search(r"## new_learnings\n(.*?)(\Z)", text, re.DOTALL)
    if not match or not match.group(1).strip():
        print("No new_learnings to review.")
        return

    new_learnings = match.group(1).strip()
    prompt = (
        "Review these staged learnings and decide which are stable patterns worth keeping:\n\n"
        f"{new_learnings}\n\n"
        "Return:\n### Promoted Patterns\n(bullet list of keepers)\n\n### Discard\n(bullet list of redundant items)"
    )
    result = call_ollama(prompt, model)

    if dry_run:
        print("\n--- Weekly Review ---")
        print(result)
        return

    promoted_match = re.search(r"### Promoted Patterns\n(.*?)(?=###|\Z)", result, re.DOTALL)
    promoted = promoted_match.group(1).strip() if promoted_match else ""

    if promoted:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        block = f"\n### Promoted {timestamp}\n\n{promoted}\n"
        text = text.replace("## new_learnings", block + "\n## new_learnings")

    text = re.sub(r"(## new_learnings\n).*", r"\1\n<!-- Auto-cleared by weekly review -->\n", text, flags=re.DOTALL)
    LONG_TERM_MEMORY.write_text(text)
    print(f"Weekly review complete. Promoted {len(promoted.splitlines())} items.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", help="Comma-separated search topics")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    parser.add_argument("--weekly-review", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.weekly_review:
        weekly_review(args.model, dry_run=args.dry_run)
        return

    topics = [t.strip() for t in args.topics.split(",")] if args.topics else DEFAULT_TOPICS
    existing_docs = load_existing_docs()

    new_count = 0
    for topic in topics:
        print(f"Searching: {topic}")
        results = ddg_search(topic)
        result = validate_finding(results, existing_docs, args.model)

        if result.get("is_new"):
            print(f"  [NEW] {result.get('one_line_summary', '')[:80]}")
            if not args.dry_run:
                append_to_new_learnings(result)
            new_count += 1
        else:
            print(f"  [SKIP] {result.get('reason', 'already known')[:80]}")

    print(f"\nResearch scout complete. {new_count} new findings stored.")


if __name__ == "__main__":
    main()
