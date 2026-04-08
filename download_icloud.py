#!/usr/bin/env python3
"""
Script pour télécharger tous les documents iCloud Drive, les organiser localement
ET créer la même structure de dossiers/sous-dossiers directement dans iCloud Drive.

Structure : Documents_Organisés/<Thème>/<Type>/[Année]/fichier
Thèmes    : Travail, Personnel, Finances, Médias

Usage: python download_icloud.py --username <apple_id>
"""

import io
import sys
import logging
import argparse
import getpass
from pathlib import Path
from datetime import datetime

try:
    from pyicloud import PyiCloudService
    from pyicloud.exceptions import PyiCloudFailedLoginException
except ImportError:
    print("Erreur: pyicloud non installé. Exécutez: pip install -r requirements.txt")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# Dossier racine créé dans iCloud Drive
ICLOUD_ROOT_FOLDER = "Documents_Organisés"

# Mots-clés dans le chemin iCloud → thème
THEME_KEYWORDS = {
    "Travail": ["travail", "pro", "boulot", "professionnel", "job", "office", "bureau", "contrat", "client"],
    "Finances": ["facture", "finance", "banque", "compta", "comptabilité", "impôt", "impot", "fiscal", "budget", "factures", "recette", "dépense"],
    "Médias": ["photo", "vidéo", "video", "image", "média", "media", "musique", "music", "souvenir"],
    "Personnel": ["personnel", "perso", "famille", "privé", "prive", "maison", "santé", "sante"],
}

# Catégorie de fichier → thème par défaut
TYPE_TO_THEME = {
    "Images": "Médias",
    "Vidéos": "Médias",
    "Audio": "Médias",
    "Tableurs": "Finances",
    "PDF": "Travail",
    "Texte": "Travail",
    "Présentations": "Travail",
    "Code": "Travail",
    "Archives": "Personnel",
    "Autres": "Personnel",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sanitize(name: str) -> str:
    forbidden = r'\/:*?"<>|'
    for ch in forbidden:
        name = name.replace(ch, "_")
    return name.strip() or "sans_titre"


def extension_category(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    categories = {
        (".pdf",): "PDF",
        (".doc", ".docx", ".odt", ".rtf", ".txt", ".pages"): "Texte",
        (".xls", ".xlsx", ".ods", ".numbers", ".csv"): "Tableurs",
        (".ppt", ".pptx", ".odp", ".key"): "Présentations",
        (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic", ".webp", ".svg"): "Images",
        (".mp4", ".mov", ".avi", ".mkv", ".m4v", ".wmv"): "Vidéos",
        (".mp3", ".m4a", ".wav", ".aac", ".flac", ".ogg"): "Audio",
        (".zip", ".tar", ".gz", ".rar", ".7z"): "Archives",
        (".py", ".js", ".ts", ".html", ".css", ".json", ".xml",
         ".yaml", ".yml", ".sh", ".swift", ".java", ".c", ".cpp", ".h"): "Code",
    }
    for extensions, category in categories.items():
        if ext in extensions:
            return category
    return "Autres"


def detect_theme(path_parts: list, category: str) -> str:
    """Détecte le thème depuis le chemin iCloud, avec fallback par type de fichier."""
    for part in path_parts:
        part_lower = part.lower()
        for theme, keywords in THEME_KEYWORDS.items():
            if any(kw in part_lower for kw in keywords):
                return theme
    return TYPE_TO_THEME.get(category, "Personnel")


def year_of(item) -> str:
    try:
        d = item.date_modified
        if d:
            return str(d.year)
    except Exception:
        pass
    return str(datetime.now().year)


# ---------------------------------------------------------------------------
# iCloud Drive — navigation
# ---------------------------------------------------------------------------

def collect_all_items(node, path_parts=None):
    """Parcourt récursivement iCloud Drive. Retourne [(item, [chemin, ...]), ...]."""
    if path_parts is None:
        path_parts = []
    items = []
    try:
        children = list(node.dir())
    except Exception as exc:
        log.warning("Impossible de lister %s : %s", "/".join(path_parts) or "/", exc)
        return items

    for name in children:
        # Ignorer le dossier qu'on crée pour éviter une boucle
        if not path_parts and name == ICLOUD_ROOT_FOLDER:
            continue
        try:
            child = node[name]
        except Exception:
            continue
        child_path = path_parts + [name]
        if hasattr(child, "dir"):
            items.extend(collect_all_items(child, child_path))
        else:
            items.append((child, child_path))

    return items


def get_or_create_icloud_folder(drive_node, folder_name: str):
    """Retourne le nœud iCloud Drive du dossier, en le créant si nécessaire."""
    try:
        existing = list(drive_node.dir())
        if folder_name in existing:
            return drive_node[folder_name]
    except Exception:
        pass
    try:
        drive_node.mkdir(folder_name)
        log.info("Dossier créé dans iCloud Drive : %s", folder_name)
        return drive_node[folder_name]
    except Exception as exc:
        log.error("Impossible de créer le dossier '%s' : %s", folder_name, exc)
        return None


# ---------------------------------------------------------------------------
# Téléchargement local
# ---------------------------------------------------------------------------

def download_item_locally(item, dest_path: Path) -> bool:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists():
        try:
            if item.size and dest_path.stat().st_size == item.size:
                log.debug("Déjà à jour localement : %s", dest_path.name)
                return True
        except Exception:
            pass
    try:
        response = item.open(stream=True)
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        log.info("Téléchargé localement : %s", dest_path.name)
        return True
    except Exception as exc:
        log.error("Échec téléchargement local %s : %s", dest_path.name, exc)
        return False


# ---------------------------------------------------------------------------
# Upload dans iCloud Drive
# ---------------------------------------------------------------------------

def upload_to_icloud(item, folder_node, filename: str) -> bool:
    """Relit le fichier depuis iCloud et l'uploade dans folder_node."""
    try:
        # Vérifier si le fichier existe déjà dans le dossier cible
        existing = list(folder_node.dir())
        if filename in existing:
            log.debug("Déjà présent dans iCloud Drive : %s", filename)
            return True

        response = item.open(stream=True)
        data = response.content  # bytes
        file_obj = io.BytesIO(data)
        file_obj.name = filename
        folder_node.upload(file_obj)
        log.info("Uploadé dans iCloud Drive : %s", filename)
        return True
    except Exception as exc:
        log.error("Échec upload iCloud %s : %s", filename, exc)
        return False


# ---------------------------------------------------------------------------
# Organisation principale
# ---------------------------------------------------------------------------

def organize(api: PyiCloudService, output_dir: Path, by_year: bool, upload: bool) -> dict:
    """
    1. Explore iCloud Drive
    2. Détecte le thème de chaque fichier (chemin iCloud → fallback par type)
    3. Télécharge localement dans output_dir/Documents_Organisés/<Thème>/<Type>/[Année]/
    4. (optionnel) Crée la même structure dans iCloud Drive
    """
    drive = api.drive

    # Dossier local racine
    local_root = output_dir / ICLOUD_ROOT_FOLDER
    local_root.mkdir(parents=True, exist_ok=True)
    log.info("Dossier local : %s", local_root)

    # Dossier iCloud Drive racine
    icloud_root = None
    if upload:
        icloud_root = get_or_create_icloud_folder(drive, ICLOUD_ROOT_FOLDER)
        if icloud_root is None:
            log.warning("Impossible de créer le dossier racine dans iCloud Drive — upload désactivé.")
            upload = False

    log.info("Exploration de iCloud Drive…")
    all_items = collect_all_items(drive)
    log.info("%d fichier(s) trouvé(s).", len(all_items))

    # Cache des nœuds iCloud Drive déjà créés pour éviter les requêtes répétées
    icloud_folder_cache: dict = {}

    stats = {"local_ok": 0, "icloud_ok": 0, "error": 0}

    for item, icloud_path in tqdm(all_items, desc="Traitement", unit="fichier"):
        filename = icloud_path[-1]
        category = sanitize(extension_category(filename))
        theme = sanitize(detect_theme(icloud_path[:-1], extension_category(filename)))

        # Chemin local : <racine>/<Thème>/<Type>/[<Année>/]<fichier>
        if by_year:
            year = year_of(item)
            local_dest = local_root / theme / category / year / sanitize(filename)
            folder_key = f"{theme}/{category}/{year}"
        else:
            local_dest = local_root / theme / category / sanitize(filename)
            folder_key = f"{theme}/{category}"

        # Téléchargement local
        ok_local = download_item_locally(item, local_dest)
        if ok_local:
            stats["local_ok"] += 1
        else:
            stats["error"] += 1

        # Upload dans iCloud Drive
        if upload and icloud_root is not None:
            if folder_key not in icloud_folder_cache:
                node = icloud_root
                for part in folder_key.split("/"):
                    node = get_or_create_icloud_folder(node, part)
                    if node is None:
                        break
                icloud_folder_cache[folder_key] = node

            target_node = icloud_folder_cache.get(folder_key)
            if target_node is not None:
                ok_icloud = upload_to_icloud(item, target_node, sanitize(filename))
                if ok_icloud:
                    stats["icloud_ok"] += 1

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Télécharge et organise tous les documents iCloud Drive, "
                    "localement ET dans iCloud Drive."
    )
    parser.add_argument("--username", "-u", required=True,
                        help="Identifiant Apple (adresse e-mail).")
    parser.add_argument("--password", "-p", default=None,
                        help="Mot de passe Apple (demandé si absent).")
    parser.add_argument("--output", "-o",
                        default=str(Path.home() / "iCloud_Backup"),
                        help="Dossier local de destination (défaut: ~/iCloud_Backup).")
    parser.add_argument("--by-year", action="store_true",
                        help="Ajouter un sous-dossier par année de modification.")
    parser.add_argument("--no-upload", action="store_true",
                        help="Ne pas créer de dossiers dans iCloud Drive (local seulement).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Logs détaillés.")
    return parser.parse_args()


def handle_2fa(api: PyiCloudService):
    if api.requires_2fa:
        code = input("Code de vérification à deux facteurs : ").strip()
        if not api.validate_2fa_code(code):
            log.error("Code 2FA invalide.")
            sys.exit(1)
        if not api.is_trusted_session:
            api.trust_session()
    elif api.requires_2sa:
        devices = api.trusted_devices
        for i, d in enumerate(devices):
            print(f"  [{i}] {d.get('deviceName', 'Appareil inconnu')}")
        idx = int(input("Appareil pour recevoir le code : "))
        device = devices[idx]
        if not api.send_verification_code(device):
            log.error("Envoi du code échoué.")
            sys.exit(1)
        code = input("Code de vérification : ").strip()
        if not api.validate_verification_code(device, code):
            log.error("Code invalide.")
            sys.exit(1)


def main():
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    password = args.password or getpass.getpass(f"Mot de passe pour {args.username} : ")

    log.info("Connexion à iCloud…")
    try:
        api = PyiCloudService(args.username, password)
    except PyiCloudFailedLoginException as exc:
        log.error("Connexion échouée : %s", exc)
        sys.exit(1)

    handle_2fa(api)
    log.info("Connexion réussie.")

    upload = not args.no_upload
    stats = organize(api, output_dir, by_year=args.by_year, upload=upload)

    icloud_path = output_dir / ICLOUD_ROOT_FOLDER
    print("\n" + "=" * 55)
    print("  Résumé")
    print("=" * 55)
    print(f"  Téléchargés localement  : {stats['local_ok']}")
    if upload:
        print(f"  Uploadés dans iCloud    : {stats['icloud_ok']}")
    print(f"  Erreurs                 : {stats['error']}")
    print(f"  Dossier local           : {icloud_path}")
    if upload:
        print(f"  Dossier iCloud Drive    : {ICLOUD_ROOT_FOLDER}/")
    print("=" * 55)
    if upload:
        print(f"\nOuvrez l'app 'Fichiers' sur votre iPhone/Mac → iCloud Drive → {ICLOUD_ROOT_FOLDER}")


if __name__ == "__main__":
    main()
