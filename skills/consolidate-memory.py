#!/usr/bin/env python3
"""
consolidate-memory skill (no API key required)
Reads the past 24hrs of Claude conversation logs from ~/.claude,
extracts key decisions, preferences, and facts via Ollama (local LLM),
and promotes important facts/patterns from recent → long-term memory.

Requirements: pip install ollama
Also requires Ollama running locally: https://ollama.com
Default model: mistral (or any model pulled via `ollama pull <model>`)

Usage:
    python skills/consolidate-memory.py
    python skills/consolidate-memory.py --model llama3
    python skills/consolidate-memory.py --promote-only
    python skills/consolidate-memory.py --dry-run
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MEMORY_DIR = REPO_ROOT / "memory"
RECENT_MEMORY = MEMORY_DIR / "recent-memory.md"
LONG_TERM_MEMORY = MEMORY_DIR / "long-term-memory.md"
PROJECT_MEMORY = MEMORY_DIR / "project-memory.md"
CLAUDE_LOGS_DIR = Path.home() / ".claude" / "projects"

DEFAULT_MODEL = "mistral"


def find_recent_logs(hours: int = 24) -> list[dict]:
    cutoff = datetime.now() - timedelta(hours=hours)
    logs = []
    if not CLAUDE_LOGS_DIR.exists():
        return logs
    for jsonl_file in CLAUDE_LOGS_DIR.rglob("*.jsonl"):
        try:
            if datetime.fromtimestamp(jsonl_file.stat().st_mtime) < cutoff:
                continue
            with open(jsonl_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except (OSError, PermissionError):
            pass
    return logs


def extract_text_from_logs(logs: list[dict]) -> str:
    parts = []
    for entry in logs:
        role = entry.get("type") or entry.get("role", "")
        content = entry.get("message", {})
        if isinstance(content, dict):
            content = content.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                c.get("text", "") if isinstance(c, dict) else str(c) for c in content
            )
        if content and role in ("human", "assistant", "user"):
            parts.append(f"[{role}]: {str(content)[:2000]}")
    return "\n".join(parts)


def call_ollama(prompt: str, model: str) -> str:
    try:
        import ollama
        response = ollama.generate(model=model, prompt=prompt)
        return response["response"]
    except Exception as e:
        print(f"  [Ollama error] {e}", file=sys.stderr)
        print("  Is Ollama running? Start with: ollama serve", file=sys.stderr)
        print(f"  Model pulled? Run: ollama pull {model}", file=sys.stderr)
        return "_Ollama unavailable — install and run: https://ollama.com_"


def consolidate_recent(logs_text: str, model: str) -> str:
    if not logs_text.strip():
        return "_No conversation logs found in the past 24 hours._"
    prompt = (
        "You are a memory consolidation assistant. Given these Claude conversation logs, "
        "extract and summarize:\n"
        "## Active Conversations\n## Recent Decisions\n## Pending Tasks\n## Context Notes\n\n"
        f"Logs:\n{logs_text[:6000]}\n\n"
        "Respond with Markdown under the four headings above. Be concise."
    )
    return call_ollama(prompt, model)


def extract_promotable_facts(recent_md: str, model: str) -> str:
    prompt = (
        "Given this recent memory snapshot, list only the facts, user preferences, "
        "and patterns stable enough for long-term storage. "
        "Return a Markdown bullet list only, or the single word NONE.\n\n"
        f"Recent memory:\n{recent_md[:3000]}"
    )
    return call_ollama(prompt, model)


def append_to_long_term(facts: str, filepath: Path) -> None:
    if facts.strip().upper() == "NONE" or not facts.strip():
        return
    timestamp = datetime.now().strftime("%Y-%m-%d")
    block = f"\n### Promoted {timestamp}\n\n{facts.strip()}\n"
    text = filepath.read_text()
    if "## new_learnings" in text:
        text = text.replace("## new_learnings", block + "\n## new_learnings")
    else:
        text = text.rstrip() + "\n" + block
    filepath.write_text(text)


def update_timestamp(filepath: Path) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    text = filepath.read_text()
    text = re.sub(r"_Last updated: .*?_", f"_Last updated: {today}_", text)
    filepath.write_text(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    parser.add_argument("--promote-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.promote_only:
        print(f"Scanning Claude logs (past 24h)...")
        logs = find_recent_logs(hours=24)
        print(f"Found {len(logs)} log entries")
        logs_text = extract_text_from_logs(logs)

        print(f"Generating recent memory summary (model: {args.model})...")
        recent_summary = consolidate_recent(logs_text, args.model)

        if args.dry_run:
            print("\n--- recent-memory.md ---")
            print(recent_summary)
        else:
            header = f"# Recent Memory (Rolling 48hr Context)\n\n_Last updated: {datetime.now().strftime('%Y-%m-%d')}_\n\n"
            RECENT_MEMORY.write_text(header + recent_summary + "\n")
            print(f"Updated {RECENT_MEMORY}")

    print("Extracting promotable facts...")
    recent_text = RECENT_MEMORY.read_text()
    promotable = extract_promotable_facts(recent_text, args.model)

    if args.dry_run:
        print("\n--- Promotable facts ---")
        print(promotable)
    else:
        append_to_long_term(promotable, LONG_TERM_MEMORY)
        update_timestamp(LONG_TERM_MEMORY)
        update_timestamp(PROJECT_MEMORY)
        print(f"Updated {LONG_TERM_MEMORY}")

    print("Memory consolidation complete.")


if __name__ == "__main__":
    main()
