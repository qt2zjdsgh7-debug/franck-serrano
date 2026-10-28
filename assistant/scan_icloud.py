#!/usr/bin/env python3
"""
Assistant personnel — lecture seule d'iCloud Drive.

Parcourt iCloud Drive, télécharge les documents susceptibles de contenir des
échéances (PDF, texte, tableurs, images de courriers) dans un cache local, et
écrit un inventaire JSON. Rien n'est modifié ni déplacé dans iCloud.

Identifiants lus dans l'environnement :
    ICLOUD_USERNAME, ICLOUD_PASSWORD
Code à deux facteurs : --code 123456 (ou saisi au clavier si absent).

Usage :
    python assistant/scan_icloud.py --list            # inventaire seul
    python assistant/scan_icloud.py --code 123456     # inventaire + téléchargement
"""

import os
import sys
import json
import argparse
from pathlib import Path

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException

DOC_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".pages", ".md",
    ".xls", ".xlsx", ".ods", ".numbers", ".csv",
    ".jpg", ".jpeg", ".png", ".heic",
}
# Dossiers sans intérêt pour les échéances
SKIP_FOLDERS = {"Documents_Organisés"}
MAX_SIZE = 25 * 1024 * 1024  # 25 Mo

COOKIE_DIR = Path(__file__).parent / ".icloud_session"
CACHE_DIR = Path(__file__).parent / "cache"


def login(code: str | None) -> PyiCloudService:
    user = os.environ.get("ICLOUD_USERNAME")
    password = os.environ.get("ICLOUD_PASSWORD")
    if not user or not password:
        sys.exit("ICLOUD_USERNAME et ICLOUD_PASSWORD doivent être définis.")
    COOKIE_DIR.mkdir(exist_ok=True)
    try:
        api = PyiCloudService(user, password, cookie_directory=str(COOKIE_DIR))
    except PyiCloudFailedLoginException as exc:
        sys.exit(f"Connexion échouée : {exc}")

    if api.requires_2fa:
        code = code or input("Code de vérification à deux facteurs : ").strip()
        if not api.validate_2fa_code(code):
            sys.exit("Code 2FA invalide.")
        if not api.is_trusted_session:
            api.trust_session()
    return api


def walk(node, parts=None):
    parts = parts or []
    try:
        names = list(node.dir())
    except Exception as exc:
        print(f"  ! impossible de lister /{'/'.join(parts)} : {exc}", file=sys.stderr)
        return
    for name in names:
        if not parts and name in SKIP_FOLDERS:
            continue
        try:
            child = node[name]
        except Exception:
            continue
        if child.type == "folder":
            yield from walk(child, parts + [name])
        else:
            yield child, parts + [name]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", help="Code 2FA reçu sur vos appareils Apple.")
    ap.add_argument("--list", action="store_true", help="Inventaire seul, sans téléchargement.")
    args = ap.parse_args()

    api = login(args.code)
    CACHE_DIR.mkdir(exist_ok=True)

    inventory = []
    for item, parts in walk(api.drive):
        path = "/".join(parts)
        ext = Path(item.name).suffix.lower()
        entry = {
            "path": path,
            "size": item.size,
            "modified": item.date_modified.isoformat() if item.date_modified else None,
            "candidate": ext in DOC_EXTENSIONS and (item.size or 0) <= MAX_SIZE,
        }
        inventory.append(entry)

        if args.list or not entry["candidate"]:
            continue
        dest = CACHE_DIR / path
        if dest.exists() and dest.stat().st_size == item.size:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with item.open(stream=True) as resp, open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)
            print(f"  ↓ {path}")
        except Exception as exc:
            print(f"  ! {path} : {exc}", file=sys.stderr)

    (CACHE_DIR / "inventaire.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2)
    )
    n = sum(e["candidate"] for e in inventory)
    print(f"{len(inventory)} fichier(s) dans iCloud Drive, dont {n} document(s) à analyser.")


if __name__ == "__main__":
    main()
