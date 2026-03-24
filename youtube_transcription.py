#!/usr/bin/env python3
"""
YouTube Video Transcription Tool
Transcrit les vidéos YouTube en texte.

Méthode 1 : Récupération des sous-titres YouTube (youtube-transcript-api)
Méthode 2 : Téléchargement audio + transcription Whisper (fallback)
"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


def extract_video_id(url_or_id: str) -> str:
    """Extrait l'ID de la vidéo depuis une URL YouTube ou retourne l'ID directement."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    # Assume it's already a video ID
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id
    raise ValueError(f"Impossible d'extraire l'ID de la vidéo depuis : {url_or_id}")


def fetch_youtube_transcript(video_id: str, languages: list[str]) -> list[dict] | None:
    """
    Tente de récupérer les sous-titres YouTube via youtube-transcript-api.
    Retourne une liste de segments ou None si indisponible.
    Compatible avec youtube-transcript-api >= 1.0.0.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=languages)
        # FetchedTranscript est itérable, chaque élément a .text et .start
        return [{"text": s.text, "start": s.start} for s in fetched]
    except ImportError:
        print("[!] youtube-transcript-api non installé. Lancez : pip install youtube-transcript-api")
        return None
    except Exception as e:
        print(f"[~] Sous-titres YouTube indisponibles ({type(e).__name__}). Passage au fallback Whisper...")
        return None


def transcribe_with_whisper(video_id: str, model_size: str = "base") -> str | None:
    """
    Télécharge l'audio de la vidéo et la transcrit avec Whisper.
    Nécessite : yt-dlp et openai-whisper
    """
    import tempfile
    import os

    try:
        import yt_dlp
    except ImportError:
        print("[!] yt-dlp non installé. Lancez : pip install yt-dlp")
        return None

    try:
        import whisper
    except ImportError:
        print("[!] openai-whisper non installé. Lancez : pip install openai-whisper")
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.%(ext)s")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": audio_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
            "quiet": True,
            "no_warnings": True,
        }

        print(f"[~] Téléchargement de l'audio (vidéo : {video_id})...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        audio_file = os.path.join(tmpdir, "audio.mp3")
        if not os.path.exists(audio_file):
            print("[!] Échec du téléchargement audio.")
            return None

        print(f"[~] Transcription avec Whisper (modèle : {model_size})...")
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_file)
        return result["text"]


def format_transcript(segments: list[dict], with_timestamps: bool = False) -> str:
    """Formate les segments de sous-titres en texte."""
    lines = []
    for seg in segments:
        if with_timestamps:
            start = seg.get("start", 0)
            minutes = int(start // 60)
            seconds = int(start % 60)
            lines.append(f"[{minutes:02d}:{seconds:02d}] {seg['text'].strip()}")
        else:
            lines.append(seg["text"].strip())
    return "\n".join(lines) if with_timestamps else " ".join(lines)


def save_transcript(text: str, output_path: Path) -> None:
    """Sauvegarde la transcription dans un fichier."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    print(f"[✓] Transcription sauvegardée : {output_path}")


def transcribe_video(
    url_or_id: str,
    output: str | None = None,
    languages: list[str] | None = None,
    timestamps: bool = False,
    whisper_model: str = "base",
    force_whisper: bool = False,
) -> str:
    """
    Transcrit une vidéo YouTube et retourne le texte.

    Args:
        url_or_id: URL YouTube ou ID de la vidéo
        output: Chemin de sortie pour le fichier texte (optionnel)
        languages: Liste de langues préférées pour les sous-titres (ex: ['fr', 'en'])
        timestamps: Inclure les horodatages dans la transcription
        whisper_model: Taille du modèle Whisper ('tiny', 'base', 'small', 'medium', 'large')
        force_whisper: Forcer l'utilisation de Whisper même si des sous-titres existent

    Returns:
        Texte de la transcription
    """
    if languages is None:
        languages = ["fr", "en"]

    video_id = extract_video_id(url_or_id)
    print(f"[*] Vidéo ID : {video_id}")

    transcript_text = None

    # Méthode 1 : Sous-titres YouTube
    if not force_whisper:
        print("[~] Tentative de récupération des sous-titres YouTube...")
        segments = fetch_youtube_transcript(video_id, languages)
        if segments:
            print(f"[✓] Sous-titres trouvés ({len(segments)} segments).")
            transcript_text = format_transcript(segments, with_timestamps=timestamps)

    # Méthode 2 : Whisper (fallback ou forcé)
    if transcript_text is None:
        transcript_text = transcribe_with_whisper(video_id, model_size=whisper_model)

    if transcript_text is None:
        print("[✗] Échec de la transcription.")
        sys.exit(1)

    # Sauvegarde optionnelle
    if output:
        save_transcript(transcript_text, Path(output))
    else:
        # Sauvegarde automatique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = Path(f"transcription_{video_id}_{timestamp}.txt")
        save_transcript(transcript_text, default_path)

    return transcript_text


def main():
    parser = argparse.ArgumentParser(
        description="Transcrit des vidéos YouTube en texte.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python youtube_transcription.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
  python youtube_transcription.py dQw4w9WgXcQ -o ma_transcription.txt
  python youtube_transcription.py <url> --languages fr en --timestamps
  python youtube_transcription.py <url> --whisper --model small
        """,
    )
    parser.add_argument("url", help="URL ou ID de la vidéo YouTube")
    parser.add_argument("-o", "--output", help="Fichier de sortie (défaut : transcription_<id>_<date>.txt)")
    parser.add_argument(
        "-l", "--languages",
        nargs="+",
        default=["fr", "en"],
        metavar="LANG",
        help="Langues préférées pour les sous-titres (défaut : fr en)",
    )
    parser.add_argument(
        "-t", "--timestamps",
        action="store_true",
        help="Inclure les horodatages [MM:SS] dans la transcription",
    )
    parser.add_argument(
        "--whisper",
        action="store_true",
        help="Forcer la transcription via Whisper (ignorer les sous-titres YouTube)",
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Taille du modèle Whisper (défaut : base)",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_output",
        help="Afficher la transcription dans le terminal",
    )

    args = parser.parse_args()

    text = transcribe_video(
        url_or_id=args.url,
        output=args.output,
        languages=args.languages,
        timestamps=args.timestamps,
        whisper_model=args.model,
        force_whisper=args.whisper,
    )

    if args.print_output:
        print("\n" + "=" * 60)
        print(text)
        print("=" * 60)


if __name__ == "__main__":
    main()
