#!/usr/bin/env python3
"""
research-scout skill
Hunts for new information that challenges or updates existing knowledge.
Searches web sources (via Brave/DuckDuckGo), cross-references against
existing docs, and stores validated findings in long-term-memory.md.

Usage:
    python skills/research-scout.py
    python skills/research-scout.py --topics "python icloud pyicloud"
    python skills/research-scout.py --weekly-review   # promote new_learnings → Confirmed Patterns
    python skills/research-scout.py --dry-run
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).parent.parent
MEMORY_DIR = REPO_ROOT / "memory"
LONG_TERM_MEMORY = MEMORY_DIR / "long-term-memory.md"
PROJECT_MEMORY = MEMORY_DIR / "project-memory.md"
README = REPO_ROOT / "README.md"

MODEL = "claude-sonnet-4-6"

DEFAULT_TOPICS = [
    "pyicloud python library updates 2025 2026",
    "iCloud Drive API changes Apple 2025",
    "python file organization automation best practices",
    "ChromaDB updates vector database 2025",
    "Gemini embedding API changes 2025",
]


def load_existing_docs() -> str:
    """Load current docs to cross-reference against findings."""
    parts = []
    for path in [README, LONG_TERM_MEMORY, PROJECT_MEMORY]:
        if path.exists():
            parts.append(f"=== {path.name} ===\n{path.read_text()[:3000]}")
    return "\n\n".join(parts)


def search_web(query: str, client: anthropic.Anthropic) -> str:
    """Use Claude's web search tool to find recent information."""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Search for recent news, updates, or changes about: {query}\n"
                        "Focus on the last 6 months. Summarize the top 3 findings with source URLs."
                    ),
                }
            ],
        )
        # Extract text from response
        texts = []
        for block in response.content:
            if hasattr(block, "text"):
                texts.append(block.text)
        return "\n".join(texts)
    except anthropic.BadRequestError:
        # Web search tool not available — fall back to knowledge-based response
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Based on your training knowledge, what are the most recent notable "
                        f"changes or updates regarding: {query}? "
                        "List up to 3 findings with approximate dates if known."
                    ),
                }
            ],
        )
        return response.content[0].text


def validate_finding(finding: str, existing_docs: str, client: anthropic.Anthropic) -> dict:
    """Cross-reference a finding against existing docs. Returns {is_new, summary}."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    "Given this new finding:\n"
                    f"{finding}\n\n"
                    "And these existing docs:\n"
                    f"{existing_docs[:4000]}\n\n"
                    "Is this finding NEW or CONTRADICTORY to the existing docs? "
                    "Reply with JSON: {\"is_new\": true/false, \"reason\": \"...\", "
                    "\"one_line_summary\": \"...\", \"source_url\": \"...\"}. "
                    "If there is no clear source URL, use null."
                ),
            }
        ],
    )
    text = response.content[0].text
    # Extract JSON from response
    import json
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"is_new": False, "reason": "parse error", "one_line_summary": "", "source_url": None}


def append_to_new_learnings(finding: dict) -> None:
    """Add a validated finding to the new_learnings section of long-term-memory.md."""
    text = LONG_TERM_MEMORY.read_text()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    source = finding.get("source_url") or "unknown"
    summary = finding.get("one_line_summary", "").strip()
    entry = f"- [{timestamp}] Source: {source} | Finding: {summary}\n"

    if "## new_learnings" in text:
        text = text.replace(
            "## new_learnings\n",
            f"## new_learnings\n\n{entry}",
        )
    else:
        text = text.rstrip() + f"\n\n## new_learnings\n\n{entry}"
    LONG_TERM_MEMORY.write_text(text)


def weekly_review(client: anthropic.Anthropic, dry_run: bool = False) -> None:
    """Promote confirmed patterns from new_learnings into Confirmed Patterns."""
    text = LONG_TERM_MEMORY.read_text()
    match = re.search(r"## new_learnings\n(.*?)(\Z)", text, re.DOTALL)
    if not match or not match.group(1).strip():
        print("No new_learnings to review.")
        return

    new_learnings = match.group(1).strip()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "Review these staged learnings:\n\n"
                    f"{new_learnings}\n\n"
                    "Which ones represent confirmed, stable patterns worth keeping long-term? "
                    "Return them as a Markdown bullet list under '### Promoted Patterns'. "
                    "Then list items to DISCARD (already known or superseded) under '### Discard'. "
                    "Use that exact heading format."
                ),
            }
        ],
    )
    review_result = response.content[0].text

    if dry_run:
        print("\n--- Weekly Review Result ---")
        print(review_result)
        return

    # Extract promoted patterns
    promoted_match = re.search(r"### Promoted Patterns\n(.*?)(?=###|\Z)", review_result, re.DOTALL)
    promoted = promoted_match.group(1).strip() if promoted_match else ""

    if promoted:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        block = f"\n### Promoted {timestamp}\n\n{promoted}\n"
        # Insert before new_learnings
        text = text.replace("## new_learnings", block + "\n## new_learnings")

    # Clear new_learnings staging area
    text = re.sub(r"(## new_learnings\n).*", r"\1\n<!-- Auto-cleared by weekly review -->\n", text, flags=re.DOTALL)
    LONG_TERM_MEMORY.write_text(text)
    print(f"Weekly review complete. Promoted {len(promoted.splitlines())} items.")


def main():
    parser = argparse.ArgumentParser(description="Research scout — find new/contradicting information")
    parser.add_argument("--topics", help="Comma-separated search topics")
    parser.add_argument("--weekly-review", action="store_true", help="Run weekly new_learnings review")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if args.weekly_review:
        weekly_review(client, dry_run=args.dry_run)
        return

    topics = [t.strip() for t in args.topics.split(",")] if args.topics else DEFAULT_TOPICS
    existing_docs = load_existing_docs()

    new_count = 0
    for topic in topics:
        print(f"Searching: {topic}")
        raw_findings = search_web(topic, client)

        result = validate_finding(raw_findings, existing_docs, client)
        if result.get("is_new"):
            print(f"  [NEW] {result.get('one_line_summary', '')}")
            if not args.dry_run:
                append_to_new_learnings(result)
            new_count += 1
        else:
            print(f"  [SKIP] {result.get('reason', 'already known')[:80]}")

    print(f"\nResearch scout complete. {new_count} new findings stored.")


if __name__ == "__main__":
    main()
