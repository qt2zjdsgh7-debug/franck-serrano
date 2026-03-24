#!/usr/bin/env python3
"""
Upload les documents du dossier local 'documents/' vers iCloud Drive.

Usage:
    python upload_docs_icloud.py --username <apple_id>
    python upload_docs_icloud.py --username <apple_id> --folder "Mes Prompts"
"""

import io
import sys
import logging
import argparse
import getpass
from pathlib import Path

try:
    from pyicloud import PyiCloudService
    from pyicloud.exceptions import PyiCloudFailedLoginException
except ImportError:
    print("Erreur: pyicloud non installé. Exécutez: pip install -r requirements.txt")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# Dossier créé dans iCloud Drive
DEFAULT_ICLOUD_FOLDER = "Prompts_Expert"

# Fichiers à uploader (depuis ./documents/)
LOCAL_DOCS_DIR = Path(__file__).parent / "documents"
EXTENSIONS_TO_UPLOAD = {".docx", ".html", ".pdf", ".md"}


def get_or_create_folder(drive_node, folder_name: str):
    """Retourne le nœud iCloud Drive, en créant le dossier si nécessaire."""
    try:
        if folder_name in list(drive_node.dir()):
            log.info("Dossier existant trouvé : %s", folder_name)
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


def upload_file(folder_node, local_path: Path) -> bool:
    """Uploade un fichier local vers un nœud iCloud Drive."""
    filename = local_path.name
    try:
        existing = list(folder_node.dir())
        if filename in existing:
            log.info("Déjà présent, ignoré : %s", filename)
            return True

        data = local_path.read_bytes()
        file_obj = io.BytesIO(data)
        file_obj.name = filename
        folder_node.upload(file_obj)
        log.info("Uploadé : %s  (%d KB)", filename, len(data) // 1024)
        return True
    except Exception as exc:
        log.error("Échec upload %s : %s", filename, exc)
        return False


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
    parser = argparse.ArgumentParser(
        description="Upload les documents locaux vers iCloud Drive."
    )
    parser.add_argument("--username", "-u", required=True,
                        help="Identifiant Apple (adresse e-mail).")
    parser.add_argument("--password", "-p", default=None,
                        help="Mot de passe Apple (demandé si absent).")
    parser.add_argument("--folder", "-f", default=DEFAULT_ICLOUD_FOLDER,
                        help=f"Nom du dossier dans iCloud Drive (défaut: {DEFAULT_ICLOUD_FOLDER}).")
    parser.add_argument("--docs-dir", default=str(LOCAL_DOCS_DIR),
                        help=f"Dossier local source (défaut: {LOCAL_DOCS_DIR}).")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        log.error("Dossier source introuvable : %s", docs_dir)
        sys.exit(1)

    # Lister les fichiers à uploader
    files = [f for f in sorted(docs_dir.iterdir())
             if f.is_file() and f.suffix.lower() in EXTENSIONS_TO_UPLOAD]

    if not files:
        log.error("Aucun fichier à uploader dans %s", docs_dir)
        sys.exit(1)

    print(f"\nFichiers à uploader ({len(files)}) :")
    for f in files:
        print(f"  • {f.name}  ({f.stat().st_size // 1024} KB)")
    print(f"\nDestination iCloud Drive : {args.folder}/\n")

    password = args.password or getpass.getpass(f"Mot de passe pour {args.username} : ")

    log.info("Connexion à iCloud…")
    try:
        api = PyiCloudService(args.username, password)
    except PyiCloudFailedLoginException as exc:
        log.error("Connexion échouée : %s", exc)
        sys.exit(1)

    handle_2fa(api)
    log.info("Connexion réussie.")

    folder_node = get_or_create_folder(api.drive, args.folder)
    if folder_node is None:
        log.error("Impossible d'accéder au dossier cible. Abandon.")
        sys.exit(1)

    ok = 0
    errors = 0
    for f in files:
        if upload_file(folder_node, f):
            ok += 1
        else:
            errors += 1

    print("\n" + "=" * 50)
    print("  Résumé upload iCloud Drive")
    print("=" * 50)
    print(f"  Uploadés avec succès : {ok}/{len(files)}")
    print(f"  Erreurs              : {errors}")
    print(f"  Dossier iCloud Drive : {args.folder}/")
    print("=" * 50)
    print(f"\nOuvrez 'Fichiers' sur votre iPhone/Mac → iCloud Drive → {args.folder}/")


if __name__ == "__main__":
    main()
