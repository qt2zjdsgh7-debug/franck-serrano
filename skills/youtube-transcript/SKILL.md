---
name: youtube-transcript
description: "Transcription et résumé de vidéos YouTube pour Franck Serrano et Aion Culture. À partir d'un lien, récupère automatiquement la transcription (script local get_transcript.py), puis la résume dans le format demandé : fiche de veille, note Aion, résumé express ou transcription nettoyée. Trilingue FR/EN/ZH. Déclencher sur : lien YouTube, youtube.com, youtu.be, shorts, transcription, transcrire une vidéo, résume cette vidéo, résumé de vidéo, que dit cette vidéo, fiche de veille vidéo, note Aion sur une vidéo, conférence YouTube, interview YouTube, documentaire, 视频摘要, 字幕."
---

# Transcription et résumé de vidéos YouTube

Franck donne un lien. Tu récupères la transcription, puis tu travailles sur le texte. Tu ne résumes **jamais** une vidéo à partir de son titre, de sa description ou de ta mémoire : uniquement à partir de la transcription récupérée.

## Étape 1 — Récupérer la transcription

Le script est dans ce skill : `scripts/get_transcript.py`.

```bash
python3 <dossier du skill>/scripts/get_transcript.py "<lien>" --horodatage
```

- Le fichier Markdown est écrit dans `~/Transcriptions_YouTube/` (le chemin est affiché). Lis-le.
- `--stdout` pour afficher sans écrire de fichier ; `--langues fr en` pour imposer l'ordre des langues ; `--sortie <dossier>` pour un autre dossier.
- Dépendance unique : `pip install youtube-transcript-api` (à installer si le script le réclame).

Le script choisit, dans l'ordre : sous-titres manuels dans la langue préférée (fr, en, zh), puis sous-titres automatiques, puis n'importe quelle langue disponible. L'en-tête du fichier indique laquelle a été prise ; signale-le si ce n'est ni manuel ni français.

### Si la récupération échoue

| Message | Cause | Que faire |
|---|---|---|
| `IpBlocked` / `RequestBlocked` | Tu tournes sur un serveur cloud : YouTube bloque ces adresses | Dis-le en une ligne. Propose de lancer le script sur l'ordinateur de Franck (Claude Code local), ou demande-lui de coller la transcription (YouTube → « … » → « Afficher la transcription ») |
| `Les sous-titres sont désactivés` | La chaîne n'a publié aucun sous-titre | Pas de transcription possible par cette voie. Le dire, ne rien inventer |
| `Vidéo indisponible` | Privée, supprimée, restreinte par âge ou par pays | Le dire |
| `Module manquant` | Bibliothèque absente | `pip install youtube-transcript-api`, puis relancer |

Si Franck colle lui-même une transcription, passe directement à l'étape 2.

## Étape 2 — Résumer selon le format demandé

Si Franck ne précise pas le format, prends la **fiche de veille**. Rédige en français, sauf demande contraire ; cite les passages clés dans la langue d'origine avec traduction entre crochets si elle n'est pas française.

### Format A — Fiche de veille (par défaut)

```markdown
# Veille vidéo — <titre>
<chaîne> · <durée> · <lien> · transcription <langue, manuelle/auto> · <date>

## En une phrase
## Points clés          (5 à 8 puces, chacune avec son repère [mm:ss])
## Noms, œuvres, lieux, chiffres cités
## Ce qui compte pour Aion   (lien avec les projets en cours : Zervos, dialogue Est-Ouest, artistes suivis par Pablo, agents Aion)
## À vérifier            (affirmations non sourcées, chiffres douteux, erreurs probables de la transcription automatique)
```

### Format B — Note Aion

Note rédigée, en prose, 1 à 2 pages : contexte (qui parle, à quel titre), thèse, arguments, intérêt pour Aion, suites à donner. Ton sobre, pas de puces sauf pour les suites à donner.

### Format C — Résumé express

Trois à cinq lignes, rien d'autre.

### Format D — Transcription nettoyée

Le texte intégral, ponctuation et paragraphes rétablis, tics de langage supprimés, intertitres ajoutés, horodatage conservé. Aucun contenu ajouté ni retiré.

## Règles

- Chaque affirmation du résumé doit pouvoir se retrouver dans la transcription ; garde les repères `[mm:ss]` pour que Franck puisse vérifier.
- Les transcriptions automatiques déforment les noms propres (artistes, collectionneurs, lieux chinois). Corrige quand tu es sûr, signale dans « À vérifier » sinon.
- Vidéo longue (plus d'une heure) : lis toute la transcription avant de résumer ; ne résume pas le premier tiers.
- Enregistre le résumé à côté de la transcription, sous le même nom suffixé `_resume.md`, sauf si Franck demande un autre emplacement (par exemple `dossiers/`).
