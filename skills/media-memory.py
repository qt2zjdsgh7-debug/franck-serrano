#!/usr/bin/env python3
"""
media-memory skill (no API key required)
Multimodal media memory using sentence-transformers (local) + ChromaDB (local).

All embeddings are computed locally — no API key needed.
Default embedding model: all-MiniLM-L6-v2 (fast, ~80MB)

Usage:
    python skills/media-memory.py ingest path/to/file.jpg --source "session"
    python skills/media-memory.py ingest-dir path/to/directory/
    python skills/media-memory.py search "sunset over the ocean" --top-k 5
    python skills/media-memory.py search "contract" --type document --after 2025-01-01
    python skills/media-memory.py show filename.pdf
"""

import argparse
import hashlib
import json
import mimetypes
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MEDIA_MEMORY_DIR = REPO_ROOT / "media-memory"
METADATA_DIR = MEDIA_MEMORY_DIR / "metadata"
CHROMA_DIR = MEDIA_MEMORY_DIR / "chroma_db"
FILES_DIR = MEDIA_MEMORY_DIR / "files"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "media_memory"

_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        print(f"  Loading embedding model ({EMBEDDING_MODEL})...")
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def embed_text(text: str) -> list[float]:
    return get_embedder().encode(text, normalize_embeddings=True).tolist()


def get_chroma_collection():
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(COLLECTION_NAME)


def get_file_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        return "other"
    major = mime.split("/")[0]
    return {"image": "image", "video": "video", "audio": "audio",
            "text": "document", "application": "document"}.get(major, "other")


def compute_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def describe_file(path: Path, file_type: str) -> dict:
    """Generate description from filename + extracted text (no LLM needed)."""
    description = f"{file_type.capitalize()} file: {path.name}"
    transcript = ""
    tags = [file_type, path.suffix.lstrip(".").lower()]

    if file_type == "document":
        if path.suffix.lower() == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                transcript = " ".join(
                    page.extract_text() for page in reader.pages[:5]
                    if page.extract_text()
                )[:3000]
                description = f"PDF document: {path.stem}. {transcript[:200]}"
            except (ImportError, Exception):
                pass
        elif path.suffix.lower() in (".txt", ".md", ".csv", ".json"):
            transcript = path.read_text(errors="ignore")[:3000]
            description = f"Text file: {path.stem}. {transcript[:200]}"

    elif file_type == "image":
        # Use filename as description — no vision model needed
        description = f"Image: {path.stem.replace('_', ' ').replace('-', ' ')}"
        tags += ["photo", "visual"]

    return {"description": description, "transcript": transcript, "tags": tags}


def ingest_file(path: Path, source: str, dry_run: bool = False) -> dict:
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return {}

    file_hash = compute_hash(path)
    file_type = get_file_type(path)
    timestamp = datetime.fromtimestamp(path.stat().st_mtime).isoformat()

    print(f"  Processing {path.name} ({file_type})...")
    desc_data = describe_file(path, file_type)

    metadata = {
        "id": file_hash,
        "filename": path.name,
        "type": file_type,
        "timestamp": timestamp,
        "ingested_at": datetime.now().isoformat(),
        "source": source,
        "description": desc_data["description"],
        "transcript": desc_data["transcript"],
        "tags": desc_data["tags"],
        "original_path": str(path),
    }

    if dry_run:
        print(json.dumps(metadata, indent=2))
        return metadata

    FILES_DIR.mkdir(parents=True, exist_ok=True)
    dest = FILES_DIR / f"{file_hash}_{path.name}"
    if not dest.exists():
        shutil.copy2(path, dest)

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    (METADATA_DIR / f"{file_hash}.json").write_text(json.dumps(metadata, indent=2))

    embed_input = (
        f"{metadata['filename']} {metadata['description']} "
        f"{metadata['transcript'][:500]} {' '.join(metadata['tags'])}"
    )
    print(f"  Embedding {path.name}...")
    vector = embed_text(embed_input)

    collection = get_chroma_collection()
    collection.upsert(
        ids=[file_hash],
        embeddings=[vector],
        metadatas=[{k: v if not isinstance(v, list) else json.dumps(v)
                    for k, v in metadata.items() if k != "id"}],
        documents=[embed_input],
    )

    print(f"  Ingested: {path.name} → {file_hash}")
    return metadata


def search(query: str, top_k: int = 5, filter_type: str = None,
           after: str = None, tags: list = None) -> list[dict]:
    query_vector = embed_text(query)
    collection = get_chroma_collection()

    count = collection.count()
    if count == 0:
        return []

    where = {}
    if filter_type:
        where["type"] = {"$eq": filter_type}
    if after:
        where["timestamp"] = {"$gte": after}

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, count),
        where=where if where else None,
        include=["metadatas", "distances", "documents"],
    )

    hits = []
    for i, meta in enumerate(results["metadatas"][0]):
        hit = dict(meta)
        hit["score"] = 1 - results["distances"][0][i]
        if "tags" in hit and isinstance(hit["tags"], str):
            try:
                hit["tags"] = json.loads(hit["tags"])
            except json.JSONDecodeError:
                pass
        if tags:
            item_tags = hit.get("tags", [])
            if isinstance(item_tags, list) and not any(
                t.lower() in [it.lower() for it in item_tags] for t in tags
            ):
                continue
        hits.append(hit)

    return hits


def main():
    parser = argparse.ArgumentParser(description="Media memory — local semantic search for files")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("ingest")
    p.add_argument("file")
    p.add_argument("--source", default="manual")
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("ingest-dir")
    p.add_argument("directory")
    p.add_argument("--source", default="directory-scan")
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--type", dest="filter_type")
    p.add_argument("--after")
    p.add_argument("--tags")

    p = sub.add_parser("show")
    p.add_argument("filename")

    args = parser.parse_args()

    if args.command == "ingest":
        ingest_file(Path(args.file), args.source, dry_run=args.dry_run)

    elif args.command == "ingest-dir":
        files = [f for f in Path(args.directory).rglob("*") if f.is_file()]
        print(f"Ingesting {len(files)} files...")
        for f in files:
            ingest_file(f, args.source, dry_run=args.dry_run)

    elif args.command == "search":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        hits = search(args.query, top_k=args.top_k, filter_type=args.filter_type,
                      after=args.after, tags=tags)
        if not hits:
            print("No results found.")
            return
        for i, hit in enumerate(hits, 1):
            print(f"\n[{i}] {hit.get('filename')} (score: {hit.get('score', 0):.3f})")
            print(f"    Type: {hit.get('type')} | Date: {hit.get('timestamp', '')[:10]}")
            print(f"    Tags: {', '.join(hit.get('tags', []))}")
            print(f"    {hit.get('description', '')[:120]}")

    elif args.command == "show":
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        for meta_file in METADATA_DIR.glob("*.json"):
            data = json.loads(meta_file.read_text())
            if args.filename in data.get("filename", "") or args.filename in data.get("id", ""):
                print(json.dumps(data, indent=2))
                return
        print(f"No metadata found for: {args.filename}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
