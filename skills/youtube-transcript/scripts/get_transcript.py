#!/usr/bin/env python3
"""Récupère la transcription d'une vidéo YouTube et l'écrit en Markdown.

Usage :
    python get_transcript.py "https://www.youtube.com/watch?v=XXXXXXXXXXX"
    python get_transcript.py XXXXXXXXXXX --langues fr en --horodatage
    python get_transcript.py URL --sortie ~/Transcriptions

Dépendance : pip install youtube-transcript-api
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )
except ImportError:
    sys.exit("Module manquant. Installez-le avec : pip install youtube-transcript-api")

LANGUES_PAR_DEFAUT = ["fr", "en", "zh-Hans", "zh-Hant", "zh", "zh-CN", "zh-TW"]


def extraire_id(lien: str) -> str:
    """Accepte un lien youtube.com, youtu.be, shorts, live ou un identifiant nu."""
    lien = lien.strip()
    if re.fullmatch(r"[\w-]{11}", lien):
        return lien
    url = urllib.parse.urlparse(lien)
    hote = url.netloc.lower().removeprefix("www.").removeprefix("m.")
    if hote == "youtu.be":
        candidat = url.path.lstrip("/").split("/")[0]
    elif hote.endswith("youtube.com"):
        params = urllib.parse.parse_qs(url.query)
        if "v" in params:
            candidat = params["v"][0]
        else:
            morceaux = [m for m in url.path.split("/") if m]
            candidat = morceaux[1] if len(morceaux) >= 2 and morceaux[0] in ("shorts", "live", "embed") else ""
    else:
        candidat = ""
    if not re.fullmatch(r"[\w-]{11}", candidat):
        sys.exit(f"Lien YouTube non reconnu : {lien}")
    return candidat


def metadonnees(video_id: str) -> dict:
    """Titre et chaîne via oEmbed (sans clé API). Vide en cas d'échec."""
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(
        f"https://www.youtube.com/watch?v={video_id}"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.load(r)
    except Exception:
        return {}


def choisir_transcription(api, video_id: str, langues: list[str]):
    """Préfère une transcription manuelle, puis automatique, puis toute autre langue disponible."""
    liste = api.list(video_id)
    try:
        return liste.find_manually_created_transcript(langues)
    except NoTranscriptFound:
        pass
    try:
        return liste.find_generated_transcript(langues)
    except NoTranscriptFound:
        pass
    # Aucune des langues demandées : on prend la première disponible.
    return next(iter(liste))


def horodatage(secondes: float) -> str:
    s = int(secondes)
    h, m, s = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def en_paragraphes(segments, avec_temps: bool, bloc: int = 60) -> str:
    """Regroupe les segments par tranches d'environ `bloc` secondes."""
    paragraphes, courant, debut = [], [], None
    for seg in segments:
        texte = seg.text.replace("\n", " ").strip()
        if not texte:
            continue
        if debut is None:
            debut = seg.start
        courant.append(texte)
        if seg.start - debut >= bloc:
            paragraphes.append((debut, " ".join(courant)))
            courant, debut = [], None
    if courant:
        paragraphes.append((debut, " ".join(courant)))
    if avec_temps:
        return "\n\n".join(f"**[{horodatage(t)}]** {p}" for t, p in paragraphes)
    return "\n\n".join(p for _, p in paragraphes)


def nom_fichier(titre: str, video_id: str) -> str:
    base = re.sub(r"[^\w\s-]", "", titre, flags=re.UNICODE).strip()
    base = re.sub(r"\s+", "_", base)[:80] or video_id
    return f"{date.today():%Y%m%d}_{base}_{video_id}.md"


def main() -> None:
    p = argparse.ArgumentParser(description="Transcription YouTube vers Markdown")
    p.add_argument("lien", help="Lien YouTube ou identifiant de la vidéo")
    p.add_argument("--langues", nargs="+", default=LANGUES_PAR_DEFAUT,
                   help="Langues par ordre de préférence (défaut : fr en zh)")
    p.add_argument("--horodatage", action="store_true",
                   help="Ajouter un repère temporel à chaque paragraphe")
    p.add_argument("--sortie", type=Path, default=Path.home() / "Transcriptions_YouTube",
                   help="Dossier de destination (défaut : ~/Transcriptions_YouTube)")
    p.add_argument("--stdout", action="store_true",
                   help="Afficher le Markdown au lieu d'écrire un fichier")
    args = p.parse_args()

    video_id = extraire_id(args.lien)
    meta = metadonnees(video_id)
    titre = meta.get("title", video_id)
    chaine = meta.get("author_name", "inconnue")

    api = YouTubeTranscriptApi()
    try:
        transcription = choisir_transcription(api, video_id, args.langues)
        segments = transcription.fetch()
    except TranscriptsDisabled:
        sys.exit("Les sous-titres sont désactivés pour cette vidéo.")
    except VideoUnavailable:
        sys.exit("Vidéo indisponible (privée, supprimée ou restreinte).")
    except StopIteration:
        sys.exit("Aucune transcription disponible pour cette vidéo.")
    except Exception as e:  # blocage IP, réseau, changement côté YouTube
        sys.exit(f"Échec de la récupération : {type(e).__name__} : {e}")

    duree = segments[-1].start + segments[-1].duration if segments else 0
    type_tr = "automatique" if transcription.is_generated else "manuelle"
    md = (
        f"# {titre}\n\n"
        f"- **Chaîne** : {chaine}\n"
        f"- **Lien** : https://www.youtube.com/watch?v={video_id}\n"
        f"- **Durée** : {horodatage(duree)}\n"
        f"- **Transcription** : {transcription.language} ({transcription.language_code}), {type_tr}\n"
        f"- **Récupérée le** : {date.today():%d/%m/%Y}\n\n"
        f"---\n\n"
        f"{en_paragraphes(segments, args.horodatage)}\n"
    )

    if args.stdout:
        print(md)
        return
    args.sortie.mkdir(parents=True, exist_ok=True)
    chemin = args.sortie / nom_fichier(titre, video_id)
    chemin.write_text(md, encoding="utf-8")
    print(chemin)


if __name__ == "__main__":
    main()
