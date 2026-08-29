#!/usr/bin/env python3
"""
Exporte un album iCloud Photos vers un dossier local, prêt à être versionné.

À EXÉCUTER SUR VOTRE MACHINE, jamais dans une session cloud : le script
demande votre mot de passe Apple et un code de double authentification.

Alternative sans code, sur Mac : Photos.app > sélectionner l'album >
Fichier > Exporter > Exporter N photos > JPEG, qualité maximale, taille pleine.

Usage:
    python export_photos_album.py --username <apple_id> --list-albums
    python export_photos_album.py --username <apple_id> --album "Manuscrits"
    python export_photos_album.py -u <apple_id> -a "Manuscrits" -o ~/Desktop/Manuscrits --jpeg
"""

import sys
import logging
import argparse
import getpass
import subprocess
import shutil
from pathlib import Path

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

HEIC_SUFFIXES = {".heic", ".heif"}


def sanitize(name: str) -> str:
    for ch in r'\/:*?"<>|':
        name = name.replace(ch, "_")
    return name.strip() or "sans_titre"


def handle_2fa(api: PyiCloudService) -> None:
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


def list_albums(api: PyiCloudService) -> None:
    print("\nAlbums disponibles :")
    for name in api.photos.albums:
        try:
            count = len(api.photos.albums[name])
        except Exception:
            count = "?"
        print(f"  - {name}  ({count} élément(s))")
    print()


def download_photo(photo, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        log.debug("Déjà présent : %s", dest.name)
        return True
    try:
        response = photo.download("original")
    except TypeError:
        response = photo.download()
    except Exception as exc:
        log.error("Échec téléchargement %s : %s", dest.name, exc)
        return False
    if response is None:
        log.error("Aucune donnée renvoyée pour %s", dest.name)
        return False
    try:
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as exc:
        log.error("Écriture impossible %s : %s", dest.name, exc)
        return False


def convert_to_jpeg(directory: Path) -> int:
    """Convertit les HEIC en JPEG via sips (macOS). Retourne le nombre converti."""
    if not shutil.which("sips"):
        log.warning("sips introuvable (hors macOS) : conversion HEIC ignorée. "
                    "Les fichiers HEIC ne sont pas exploitables tels quels.")
        return 0
    jpeg_dir = directory / "jpeg"
    jpeg_dir.mkdir(exist_ok=True)
    converted = 0
    for src in sorted(directory.iterdir()):
        if src.suffix.lower() not in HEIC_SUFFIXES:
            continue
        dest = jpeg_dir / (src.stem + ".jpg")
        if dest.exists():
            continue
        result = subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "90",
             str(src), "--out", str(dest)],
            capture_output=True,
        )
        if result.returncode == 0:
            converted += 1
        else:
            log.error("Conversion échouée pour %s", src.name)
    if converted:
        log.info("%d fichier(s) converti(s) en JPEG dans %s", converted, jpeg_dir)
    return converted


def export_album(api: PyiCloudService, album_name: str, output_dir: Path) -> dict:
    try:
        album = api.photos.albums[album_name]
    except KeyError:
        log.error("Album introuvable : %s", album_name)
        log.info("Utilisez --list-albums pour voir les albums disponibles.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    log.info("Export de l'album « %s » vers %s", album_name, output_dir)

    stats = {"ok": 0, "error": 0}
    photos = list(album)
    log.info("%d élément(s) dans l'album.", len(photos))

    width = max(3, len(str(len(photos))))
    for index, photo in enumerate(tqdm(photos, desc="Export", unit="photo"), start=1):
        filename = sanitize(getattr(photo, "filename", f"photo_{index}.jpg"))
        # Préfixe numérique : préserve l'ordre de l'album, qui porte souvent
        # le regroupement par document (recto, verso, détail).
        dest = output_dir / f"{index:0{width}d}_{filename}"
        if download_photo(photo, dest):
            stats["ok"] += 1
        else:
            stats["error"] += 1
    return stats


def parse_args():
    parser = argparse.ArgumentParser(
        description="Exporte un album iCloud Photos vers un dossier local."
    )
    parser.add_argument("--username", "-u", required=True,
                        help="Identifiant Apple (adresse e-mail).")
    parser.add_argument("--password", "-p", default=None,
                        help="Mot de passe Apple (demandé si absent).")
    parser.add_argument("--album", "-a", default=None,
                        help="Nom exact de l'album à exporter.")
    parser.add_argument("--list-albums", action="store_true",
                        help="Lister les albums disponibles et quitter.")
    parser.add_argument("--output", "-o",
                        default=str(Path.home() / "Desktop" / "Export_Photos"),
                        help="Dossier local de destination.")
    parser.add_argument("--jpeg", action="store_true",
                        help="Convertir les HEIC en JPEG après export (macOS, via sips).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Logs détaillés.")
    args = parser.parse_args()
    if not args.list_albums and not args.album:
        parser.error("Indiquez --album NOM, ou --list-albums pour voir les albums.")
    return args


def main():
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    password = args.password or getpass.getpass(f"Mot de passe pour {args.username} : ")

    log.info("Connexion à iCloud…")
    try:
        api = PyiCloudService(args.username, password)
    except PyiCloudFailedLoginException as exc:
        log.error("Connexion échouée : %s", exc)
        sys.exit(1)

    handle_2fa(api)
    log.info("Connexion réussie.")

    if args.list_albums:
        list_albums(api)
        return

    output_dir = Path(args.output).expanduser().resolve()
    stats = export_album(api, args.album, output_dir)

    if args.jpeg:
        convert_to_jpeg(output_dir)

    print("\n" + "=" * 55)
    print("  Résumé de l'export")
    print("=" * 55)
    print(f"  Exportés  : {stats['ok']}")
    print(f"  Erreurs   : {stats['error']}")
    print(f"  Dossier   : {output_dir}")
    print("=" * 55)
    print("\nÉtape suivante : copier les JPEG dans manuscrits/01_sources/,")
    print("puis git add / commit / push.")


if __name__ == "__main__":
    main()
