#!/usr/bin/env python3
"""
consolidate-memory skill
Reads the past 24hrs of Claude conversation logs from ~/.claude,
extracts key decisions, preferences, and facts, updates memory files,
and promotes important facts/patterns from recent → long-term memory.

Usage:
    python skills/consolidate-memory.py
    python skills/consolidate-memory.py --promote-only   # only promote recent → long-term
    python skills/consolidate-memory.py --dry-run        # show what would change
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).parent.parent
MEMORY_DIR = REPO_ROOT / "memory"
RECENT_MEMORY = MEMORY_DIR / "recent-memory.md"
LONG_TERM_MEMORY = MEMORY_DIR / "long-term-memory.md"
PROJECT_MEMORY = MEMORY_DIR / "project-memory.md"
CLAUDE_LOGS_DIR = Path.home() / ".claude" / "projects"

MODEL = "claude-sonnet-4-6"


def find_recent_logs(hours: int = 24) -> list[dict]:
    """Scan ~/.claude/projects for conversation logs from the past N hours."""
    cutoff = datetime.now() - timedelta(hours=hours)
    logs = []

    if not CLAUDE_LOGS_DIR.exists():
        print(f"No Claude logs directory found at {CLAUDE_LOGS_DIR}", file=sys.stderr)
        return logs

    for jsonl_file in CLAUDE_LOGS_DIR.rglob("*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
            if mtime < cutoff:
                continue
            with open(jsonl_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        entry["_source_file"] = str(jsonl_file)
                        logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        except (OSError, PermissionError):
            continue

    return logs


def extract_text_from_logs(logs: list[dict]) -> str:
    """Pull human/assistant message text from raw log entries."""
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


def call_claude(system: str, user: str, client: anthropic.Anthropic) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def consolidate_recent(logs_text: str, client: anthropic.Anthropic) -> str:
    """Use Claude to extract a rolling 48hr context summary."""
    system = (
        "You are a memory consolidation assistant. Given raw Claude conversation logs, "
        "extract: (1) Active conversations and their status, (2) Key decisions made, "
        "(3) Pending tasks, (4) Important context notes. "
        "Format your response as Markdown under these four headings. Be concise."
    )
    if not logs_text.strip():
        return "_No conversation logs found in the past 24 hours._"
    return call_claude(system, f"Logs:\n\n{logs_text[:8000]}", client)


def extract_promotable_facts(recent_md: str, client: anthropic.Anthropic) -> str:
    """Identify facts/patterns from recent memory worth promoting to long-term."""
    system = (
        "You are a memory curator. Given a recent-memory snapshot, identify facts, "
        "user preferences, and confirmed patterns that are stable enough for long-term storage. "
        "Return ONLY a Markdown bullet list (no headings). If nothing is promotable, return 'NONE'."
    )
    return call_claude(system, f"Recent memory:\n\n{recent_md}", client)


def update_file_section(filepath: Path, section_header: str, new_content: str) -> None:
    """Replace the content under a markdown section header."""
    text = filepath.read_text()
    # Match from header to next ## header or end of file
    pattern = re.compile(
        rf"(## {re.escape(section_header)}\n)(.*?)(\n## |\Z)", re.DOTALL
    )
    replacement = rf"\g<1>\n{new_content}\n\g<3>"
    new_text, n = pattern.subn(replacement, text)
    if n == 0:
        # Section not found — append it
        new_text = text.rstrip() + f"\n\n## {section_header}\n\n{new_content}\n"
    filepath.write_text(new_text)


def append_to_long_term(facts: str, filepath: Path) -> None:
    """Append promoted facts under Confirmed Patterns in long-term memory."""
    if facts.strip() == "NONE" or not facts.strip():
        return
    timestamp = datetime.now().strftime("%Y-%m-%d")
    block = f"\n### Promoted {timestamp}\n\n{facts.strip()}\n"
    text = filepath.read_text()
    # Insert before new_learnings section
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
    parser = argparse.ArgumentParser(description="Consolidate Claude memory files")
    parser.add_argument("--promote-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if not args.promote_only:
        print("Scanning Claude logs (past 24h)...")
        logs = find_recent_logs(hours=24)
        print(f"Found {len(logs)} log entries")
        logs_text = extract_text_from_logs(logs)

        print("Generating recent memory summary...")
        recent_summary = consolidate_recent(logs_text, client)

        if args.dry_run:
            print("\n--- recent-memory.md (new content) ---")
            print(recent_summary)
        else:
            for section in ["Active Conversations", "Recent Decisions", "Pending Tasks", "Context Notes"]:
                # Clear old auto-content; consolidate_recent returns all sections
                pass
            # Overwrite main body while preserving header
            header = "# Recent Memory (Rolling 48hr Context)\n\n"
            timestamp_line = f"_Last updated: {datetime.now().strftime('%Y-%m-%d')}_\n\n"
            RECENT_MEMORY.write_text(header + timestamp_line + recent_summary + "\n")
            print(f"Updated {RECENT_MEMORY}")

    print("Extracting promotable facts for long-term memory...")
    recent_text = RECENT_MEMORY.read_text()
    promotable = extract_promotable_facts(recent_text, client)

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
