#!/usr/bin/env python3
"""
Script pour télécharger tous les documents iCloud et les organiser en dossiers/sous-dossiers.
Usage: python download_icloud.py --username <apple_id> --output <dossier_local>
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

try:
    from pyicloud import PyiCloudService
    from pyicloud.exceptions import PyiCloudFailedLoginException, PyiCloudAPIResponseException
except ImportError:
    print("Erreur: pyicloud non installé. Exécutez: pip install -r requirements.txt")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    # Fallback si tqdm n'est pas disponible
    def tqdm(iterable, **kwargs):
        return iterable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sanitize(name: str) -> str:
    """Remplace les caractères interdits dans un nom de fichier/dossier."""
    forbidden = r'\/:*?"<>|'
    for ch in forbidden:
        name = name.replace(ch, "_")
    return name.strip() or "sans_titre"


def extension_category(filename: str) -> str:
    """Retourne la catégorie (sous-dossier) en fonction de l'extension."""
    ext = Path(filename).suffix.lower()
    categories = {
        # Documents texte
        (".pdf",): "PDF",
        (".doc", ".docx", ".odt", ".rtf", ".txt", ".pages"): "Texte",
        # Tableurs
        (".xls", ".xlsx", ".ods", ".numbers", ".csv"): "Tableurs",
        # Présentations
        (".ppt", ".pptx", ".odp", ".key"): "Présentations",
        # Images
        (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic", ".webp", ".svg"): "Images",
        # Vidéos
        (".mp4", ".mov", ".avi", ".mkv", ".m4v", ".wmv"): "Vidéos",
        # Audio
        (".mp3", ".m4a", ".wav", ".aac", ".flac", ".ogg"): "Audio",
        # Archives
        (".zip", ".tar", ".gz", ".rar", ".7z"): "Archives",
        # Code
        (".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml",
         ".sh", ".bash", ".swift", ".java", ".c", ".cpp", ".h"): "Code",
    }
    for extensions, category in categories.items():
        if ext in extensions:
            return category
    return "Autres"


def year_subfolder(item) -> str:
    """Retourne l'année de modification de l'item iCloud."""
    try:
        date_modified = item.date_modified
        if date_modified:
            return str(date_modified.year)
    except Exception:
        pass
    return str(datetime.now().year)


# ---------------------------------------------------------------------------
# iCloud Drive traversal
# ---------------------------------------------------------------------------

def collect_all_items(node, path_parts=None):
    """
    Parcourt récursivement l'arbre iCloud Drive et retourne une liste de
    tuples (item, chemin_relatif_dans_icloud).
    """
    if path_parts is None:
        path_parts = []

    items = []
    try:
        children = list(node.dir())
    except Exception as exc:
        log.warning("Impossible de lister %s : %s", "/".join(path_parts) or "/", exc)
        return items

    for name in children:
        try:
            child = node[name]
        except Exception:
            continue

        child_path = path_parts + [name]

        # Dossier → descente récursive
        if hasattr(child, "dir"):
            items.extend(collect_all_items(child, child_path))
        else:
            items.append((child, child_path))

    return items


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def download_item(item, dest_path: Path) -> bool:
    """Télécharge un fichier iCloud vers dest_path. Retourne True si réussi."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Évite de re-télécharger si déjà présent et de même taille
    if dest_path.exists():
        try:
            remote_size = item.size
            if remote_size and dest_path.stat().st_size == remote_size:
                log.debug("Déjà à jour : %s", dest_path)
                return True
        except Exception:
            pass

    try:
        response = item.open(stream=True)
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)
        log.info("Téléchargé : %s", dest_path)
        return True
    except Exception as exc:
        log.error("Échec du téléchargement de %s : %s", dest_path, exc)
        return False


# ---------------------------------------------------------------------------
# Main organisation logic
# ---------------------------------------------------------------------------

def organize_and_download(api: PyiCloudService, output_dir: Path, by_year: bool) -> dict:
    """
    Structure dans output_dir :
        iCloud_Documents/
            <Catégorie>/          (ex: PDF, Images, Texte …)
                [<Année>/]        (optionnel, si --by-year)
                    fichier.ext
    """
    root_folder = output_dir / "iCloud_Documents"
    root_folder.mkdir(parents=True, exist_ok=True)
    log.info("Dossier racine : %s", root_folder)

    log.info("Exploration de iCloud Drive…")
    drive = api.drive
    all_items = collect_all_items(drive)
    log.info("%d fichier(s) trouvé(s) dans iCloud Drive.", len(all_items))

    stats = {"success": 0, "skipped": 0, "error": 0}

    for item, icloud_path in tqdm(all_items, desc="Téléchargement", unit="fichier"):
        filename = icloud_path[-1]
        category = extension_category(filename)

        if by_year:
            year = year_subfolder(item)
            dest = root_folder / sanitize(category) / year / sanitize(filename)
        else:
            dest = root_folder / sanitize(category) / sanitize(filename)

        ok = download_item(item, dest)
        if ok:
            stats["success"] += 1
        else:
            stats["error"] += 1

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Télécharge et organise tous les documents iCloud Drive."
    )
    parser.add_argument(
        "--username", "-u",
        required=True,
        help="Identifiant Apple (adresse e-mail).",
    )
    parser.add_argument(
        "--password", "-p",
        default=None,
        help="Mot de passe Apple. Si omis, sera demandé interactivement.",
    )
    parser.add_argument(
        "--output", "-o",
        default=str(Path.home() / "iCloud_Backup"),
        help="Dossier de destination local (défaut: ~/iCloud_Backup).",
    )
    parser.add_argument(
        "--by-year",
        action="store_true",
        help="Créer un sous-dossier par année de modification.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Afficher les messages de débogage.",
    )
    return parser.parse_args()


def prompt_2fa(api: PyiCloudService):
    """Gère la double authentification si nécessaire."""
    if api.requires_2fa:
        code = input("Entrez le code de vérification à deux facteurs : ").strip()
        result = api.validate_2fa_code(code)
        if not result:
            log.error("Code 2FA invalide.")
            sys.exit(1)
        if not api.is_trusted_session:
            api.trust_session()
    elif api.requires_2sa:
        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print(f"[{i}] {device.get('deviceName', 'Appareil inconnu')}")
        idx = int(input("Choisissez un appareil pour recevoir le code : "))
        device = devices[idx]
        if not api.send_verification_code(device):
            log.error("Impossible d'envoyer le code.")
            sys.exit(1)
        code = input("Entrez le code de vérification : ").strip()
        if not api.validate_verification_code(device, code):
            log.error("Code invalide.")
            sys.exit(1)


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Mot de passe
    password = args.password
    if not password:
        import getpass
        password = getpass.getpass(f"Mot de passe pour {args.username} : ")

    # Connexion
    log.info("Connexion à iCloud en tant que %s…", args.username)
    try:
        api = PyiCloudService(args.username, password)
    except PyiCloudFailedLoginException as exc:
        log.error("Connexion échouée : %s", exc)
        sys.exit(1)

    # Double authentification
    prompt_2fa(api)

    log.info("Connexion réussie.")

    # Téléchargement et organisation
    stats = organize_and_download(api, output_dir, by_year=args.by_year)

    # Résumé
    print("\n" + "=" * 50)
    print("Résumé du téléchargement")
    print("=" * 50)
    print(f"  Réussi  : {stats['success']}")
    print(f"  Erreurs : {stats['error']}")
    print(f"  Dossier : {output_dir / 'iCloud_Documents'}")
    print("=" * 50)


if __name__ == "__main__":
    main()
