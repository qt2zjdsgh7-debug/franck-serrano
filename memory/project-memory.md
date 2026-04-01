# Project Memory (Active State)

_Last updated: 2026-04-01_

## Current Project: iCloud Drive Downloader

### Status
- Core download + organize script: `download_icloud.py` — complete
- Requirements: `requirements.txt`

### Architecture

```
franck-serrano/
├── download_icloud.py       # Main downloader/organizer
├── requirements.txt
├── memory/                  # Persistent memory layer
│   ├── recent-memory.md
│   ├── long-term-memory.md
│   └── project-memory.md
├── skills/                  # Automation skills
│   ├── consolidate-memory.py
│   ├── research-scout.py
│   └── media-memory.py
├── media-memory/            # Multimodal media index
│   └── metadata/
└── CLAUDE.md
```

### Open Items

<!-- Active TODOs and in-flight work -->

### Key Files

| File | Purpose |
|------|---------|
| `download_icloud.py` | Downloads and organizes iCloud Drive files |
| `skills/consolidate-memory.py` | Nightly memory consolidation |
| `skills/research-scout.py` | Finds new contradicting/updating information |
| `skills/media-memory.py` | Multimodal media ingestion + semantic search |
