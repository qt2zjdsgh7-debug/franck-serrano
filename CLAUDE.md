# CLAUDE.md

This file is loaded automatically by Claude Code at session start.

## Memory System

### Recent Memory (auto-loaded)

<!-- recent-memory.md is included inline below at startup -->

@memory/recent-memory.md

### Long-Term Memory

See [memory/long-term-memory.md](memory/long-term-memory.md) for distilled facts,
user preferences, confirmed patterns, and staged `new_learnings`.

### Project Memory

See [memory/project-memory.md](memory/project-memory.md) for active project state,
architecture, and open items.

---

## Automatic Behaviors

### Media Logging

When a user sends a media file (image, video, audio) OR Claude generates one:
1. Run `python skills/media-memory.py ingest <file> --source "session"` to log it.
2. Before answering questions that might relate to past media, run a search:
   `python skills/media-memory.py search "<relevant query>" --top-k 3`
   and surface any relevant past assets.

### Memory Queries

When a past asset or fact *seems relevant* to the current task, query the memory
system before responding:
- Semantic search: `python skills/media-memory.py search "<query>"`
- Check recent context: read `memory/recent-memory.md`
- Check long-term facts: read `memory/long-term-memory.md`

---

## Scheduled Tasks (run manually or via cron)

| Task | Command | Schedule |
|------|---------|----------|
| Consolidate memory | `python skills/consolidate-memory.py` | Nightly |
| Research scout | `python skills/research-scout.py` | 3× nightly |
| Weekly learning review | `python skills/research-scout.py --weekly-review` | Weekly |

### Cron setup (example)

```cron
# Consolidate memory nightly at 02:00
0 2 * * * cd /path/to/franck-serrano && python skills/consolidate-memory.py

# Research scout 3× nightly (23:00, 03:00, 07:00)
0 23 * * * cd /path/to/franck-serrano && python skills/research-scout.py
0 3  * * * cd /path/to/franck-serrano && python skills/research-scout.py
0 7  * * * cd /path/to/franck-serrano && python skills/research-scout.py

# Weekly review every Sunday at 08:00
0 8 * * 0 cd /path/to/franck-serrano && python skills/research-scout.py --weekly-review
```

---

## Required Setup (No API Keys Needed)

| Dependency | Used by | Install |
|-----------|---------|---------|
| **Ollama** (local LLM) | consolidate-memory, research-scout | https://ollama.com → `ollama pull mistral` |
| **sentence-transformers** | media-memory (local embeddings) | `pip install sentence-transformers` |
| **ChromaDB** | media-memory (vector DB) | `pip install chromadb` |
| **duckduckgo-search** | research-scout (free web search) | `pip install duckduckgo-search` |

---

## Project Context

- **Repo**: qt2zjdsgh7-debug/franck-serrano
- **Dev branch**: `claude/new-session-gtv1n`
- **Main script**: `download_icloud.py` — downloads and organizes iCloud Drive files
- **Language**: Python 3.10+
