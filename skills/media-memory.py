#!/usr/bin/env python3
"""
media-memory skill
Multimodal media memory system using Gemini Embedding 2 + ChromaDB.

Stores every media file (images, video, audio, documents) in /media-memory
with a metadata schema: filename, type, timestamp, source, natural language
description, extracted text/transcript, and semantic tags.

Each item is embedded with Gemini Embedding 2 and stored in a local ChromaDB.

Usage:
    # Ingest a file
    python skills/media-memory.py ingest path/to/file.jpg --source "user upload"

    # Ingest a directory
    python skills/media-memory.py ingest-dir path/to/directory/

    # Semantic search
    python skills/media-memory.py search "sunset over the ocean" --top-k 5

    # Filtered search (type + date range + tags)
    python skills/media-memory.py search "contract" --type document --after 2025-01-01

    # Show metadata for a file
    python skills/media-memory.py show filename.pdf
"""

import argparse
import hashlib
import json
import mimetypes
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MEDIA_MEMORY_DIR = REPO_ROOT / "media-memory"
METADATA_DIR = MEDIA_MEMORY_DIR / "metadata"
CHROMA_DIR = MEDIA_MEMORY_DIR / "chroma_db"
FILES_DIR = MEDIA_MEMORY_DIR / "files"

GEMINI_EMBEDDING_MODEL = "models/text-embedding-004"  # Gemini Embedding 2
COLLECTION_NAME = "media_memory"


def get_file_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        return "other"
    major = mime.split("/")[0]
    type_map = {
        "image": "image",
        "video": "video",
        "audio": "audio",
        "text": "document",
        "application": "document",
    }
    return type_map.get(major, "other")


def compute_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def describe_file(path: Path, file_type: str, client) -> dict:
    """Use Gemini to generate a natural language description and extract tags/transcript."""
    import google.generativeai as genai

    description = ""
    transcript = ""
    tags = []

    try:
        if file_type == "image":
            model = genai.GenerativeModel("gemini-2.0-flash")
            with open(path, "rb") as f:
                image_data = f.read()
            import base64
            b64 = base64.b64encode(image_data).decode()
            mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
            response = model.generate_content([
                {"mime_type": mime, "data": b64},
                "Describe this image in 2-3 sentences. Then list 5-10 semantic tags as a JSON array called 'tags'.",
            ])
            text = response.text
            # Parse tags
            import re
            tags_match = re.search(r'"tags"\s*:\s*(\[.*?\])', text, re.DOTALL)
            if tags_match:
                tags = json.loads(tags_match.group(1))
            description = re.sub(r'"tags"\s*:.*', "", text, flags=re.DOTALL).strip()

        elif file_type in ("audio", "video"):
            # For audio/video, use file metadata and name for now
            description = f"{file_type.capitalize()} file: {path.name}"
            tags = [file_type, path.suffix.lstrip(".")]

        elif file_type == "document":
            # Try to extract text for PDFs/text files
            if path.suffix.lower() == ".pdf":
                try:
                    import pypdf
                    reader = pypdf.PdfReader(str(path))
                    text_content = " ".join(
                        page.extract_text() for page in reader.pages[:5] if page.extract_text()
                    )[:2000]
                    transcript = text_content
                except ImportError:
                    transcript = ""
            elif path.suffix.lower() in (".txt", ".md", ".csv"):
                transcript = path.read_text(errors="ignore")[:2000]

            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = (
                f"File: {path.name}\nContent preview: {transcript[:500] or '(binary)'}\n"
                "Describe this document in 2 sentences. List 5 semantic tags as JSON array 'tags'."
            )
            response = model.generate_content(prompt)
            text = response.text
            import re
            tags_match = re.search(r'"tags"\s*:\s*(\[.*?\])', text, re.DOTALL)
            if tags_match:
                tags = json.loads(tags_match.group(1))
            description = re.sub(r'"tags"\s*:.*', "", text, flags=re.DOTALL).strip()

        else:
            description = f"File: {path.name}"
            tags = [path.suffix.lstrip(".") or "unknown"]

    except Exception as e:
        description = f"File: {path.name} (description unavailable: {e})"
        tags = [file_type]

    return {"description": description, "transcript": transcript, "tags": tags}


def embed_text(text: str) -> list[float]:
    """Embed text using Gemini Embedding 2."""
    import google.generativeai as genai
    result = genai.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def get_chroma_collection():
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(COLLECTION_NAME)


def ingest_file(path: Path, source: str, dry_run: bool = False) -> dict:
    """Ingest a single file into media-memory."""
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY or GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    genai.configure(api_key=api_key)

    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return {}

    file_hash = compute_hash(path)
    file_type = get_file_type(path)
    timestamp = datetime.fromtimestamp(path.stat().st_mtime).isoformat()

    print(f"  Describing {path.name} ({file_type})...")
    description_data = describe_file(path, file_type, genai)

    metadata = {
        "id": file_hash,
        "filename": path.name,
        "type": file_type,
        "timestamp": timestamp,
        "ingested_at": datetime.now().isoformat(),
        "source": source,
        "description": description_data["description"],
        "transcript": description_data["transcript"],
        "tags": description_data["tags"],
        "original_path": str(path),
    }

    if dry_run:
        print(json.dumps(metadata, indent=2))
        return metadata

    # Copy file into media-memory/files/
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    dest = FILES_DIR / f"{file_hash}_{path.name}"
    if not dest.exists():
        shutil.copy2(path, dest)

    # Save metadata JSON
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = METADATA_DIR / f"{file_hash}.json"
    meta_path.write_text(json.dumps(metadata, indent=2))

    # Embed and store in ChromaDB
    embed_text_input = (
        f"{metadata['filename']} {metadata['description']} "
        f"{metadata['transcript'][:500]} {' '.join(metadata['tags'])}"
    )
    print(f"  Embedding {path.name}...")
    vector = embed_text(embed_text_input)

    collection = get_chroma_collection()
    collection.upsert(
        ids=[file_hash],
        embeddings=[vector],
        metadatas=[{k: v if not isinstance(v, list) else json.dumps(v)
                    for k, v in metadata.items() if k != "id"}],
        documents=[embed_text_input],
    )

    print(f"  Ingested: {path.name} → {file_hash}")
    return metadata


def search(query: str, top_k: int = 5, filter_type: str = None,
           after: str = None, tags: list[str] = None) -> list[dict]:
    """Semantic search with optional metadata filtering."""
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY or GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    genai.configure(api_key=api_key)

    query_vector = embed_text(query)

    collection = get_chroma_collection()

    where = {}
    if filter_type:
        where["type"] = {"$eq": filter_type}
    if after:
        where["timestamp"] = {"$gte": after}

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count() or 1),
        where=where if where else None,
        include=["metadatas", "distances", "documents"],
    )

    hits = []
    for i, meta in enumerate(results["metadatas"][0]):
        hit = dict(meta)
        hit["score"] = 1 - results["distances"][0][i]  # cosine similarity
        if "tags" in hit and isinstance(hit["tags"], str):
            try:
                hit["tags"] = json.loads(hit["tags"])
            except json.JSONDecodeError:
                pass
        # Filter by tags post-query if needed
        if tags:
            item_tags = hit.get("tags", [])
            if isinstance(item_tags, list):
                if not any(t.lower() in [it.lower() for it in item_tags] for t in tags):
                    continue
        hits.append(hit)

    return hits


def main():
    parser = argparse.ArgumentParser(description="Media memory — ingest and search multimodal files")
    subparsers = parser.add_subparsers(dest="command")

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Ingest a single file")
    p_ingest.add_argument("file", help="Path to file")
    p_ingest.add_argument("--source", default="manual", help="Source label")
    p_ingest.add_argument("--dry-run", action="store_true")

    # ingest-dir
    p_ingest_dir = subparsers.add_parser("ingest-dir", help="Ingest all files in a directory")
    p_ingest_dir.add_argument("directory", help="Directory path")
    p_ingest_dir.add_argument("--source", default="directory-scan")
    p_ingest_dir.add_argument("--dry-run", action="store_true")

    # search
    p_search = subparsers.add_parser("search", help="Semantic search")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--top-k", type=int, default=5)
    p_search.add_argument("--type", dest="filter_type", help="Filter by type: image/video/audio/document")
    p_search.add_argument("--after", help="Filter by date (YYYY-MM-DD)")
    p_search.add_argument("--tags", help="Comma-separated tags to filter")

    # show
    p_show = subparsers.add_parser("show", help="Show metadata for a file")
    p_show.add_argument("filename", help="Filename to look up")

    args = parser.parse_args()

    if args.command == "ingest":
        ingest_file(Path(args.file), args.source, dry_run=args.dry_run)

    elif args.command == "ingest-dir":
        directory = Path(args.directory)
        files = [f for f in directory.rglob("*") if f.is_file()]
        print(f"Ingesting {len(files)} files from {directory}")
        for f in files:
            ingest_file(f, args.source, dry_run=args.dry_run)

    elif args.command == "search":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        hits = search(args.query, top_k=args.top_k, filter_type=args.filter_type,
                      after=args.after, tags=tags)
        if not hits:
            print("No results found.")
        for i, hit in enumerate(hits, 1):
            score = hit.get("score", 0)
            print(f"\n[{i}] {hit.get('filename')} (score: {score:.3f})")
            print(f"    Type: {hit.get('type')} | Date: {hit.get('timestamp', '')[:10]}")
            print(f"    Tags: {', '.join(hit.get('tags', []))}")
            print(f"    {hit.get('description', '')[:120]}")

    elif args.command == "show":
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        matches = list(METADATA_DIR.glob("*.json"))
        found = False
        for meta_file in matches:
            data = json.loads(meta_file.read_text())
            if args.filename in data.get("filename", "") or args.filename in data.get("id", ""):
                print(json.dumps(data, indent=2))
                found = True
        if not found:
            print(f"No metadata found for: {args.filename}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
