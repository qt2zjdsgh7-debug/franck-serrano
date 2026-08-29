# Téléchargement et organisation iCloud Drive

Script Python qui :
1. **Télécharge** tous les documents de votre iCloud Drive en local
2. **Crée automatiquement** les dossiers et sous-dossiers organisés **directement dans iCloud Drive**

Après exécution, ouvrez l'app **Fichiers** sur iPhone/iPad ou le Finder sur Mac → **iCloud Drive** → `Documents_Organisés/`

## Structure des dossiers créés (locale ET dans iCloud Drive)

```
Documents_Organisés/
├── PDF/
│   ├── document1.pdf
│   └── document2.pdf
├── Texte/
│   ├── note.docx
│   └── rapport.pages
├── Tableurs/
│   └── budget.xlsx
├── Présentations/
│   └── presentation.key
├── Images/
│   └── photo.heic
├── Vidéos/
│   └── film.mov
├── Audio/
│   └── musique.m4a
├── Archives/
│   └── backup.zip
├── Code/
│   └── script.py
└── Autres/
    └── fichier_inconnu.xyz
```

Avec l'option `--by-year`, un sous-dossier par année est ajouté :

```
Documents_Organisés/
├── PDF/
│   ├── 2023/
│   │   └── contrat.pdf
│   └── 2024/
│       └── facture.pdf
└── Images/
    └── 2025/
        └── photo.heic
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# Par défaut : télécharge localement ET crée les dossiers dans iCloud Drive
python download_icloud.py --username votre@apple.com

# Avec sous-dossiers par année
python download_icloud.py --username votre@apple.com --by-year

# Local seulement (sans créer de dossiers dans iCloud Drive)
python download_icloud.py --username votre@apple.com --no-upload

# Dossier local personnalisé
python download_icloud.py --username votre@apple.com --output ~/Bureau/MesDocuments
```

## Options

| Option | Description |
|--------|-------------|
| `--username` / `-u` | Identifiant Apple (obligatoire) |
| `--password` / `-p` | Mot de passe Apple (demandé si absent) |
| `--output` / `-o` | Dossier local de destination (défaut: `~/iCloud_Backup`) |
| `--by-year` | Créer un sous-dossier par année de modification |
| `--no-upload` | Ne pas créer de dossiers dans iCloud Drive |
| `--verbose` / `-v` | Activer les logs détaillés |

## Double authentification (2FA)

Si votre compte utilise la double authentification, le script vous demandera automatiquement le code de vérification envoyé à votre appareil Apple.

## Catégories de fichiers

| Catégorie | Extensions |
|-----------|------------|
| PDF | .pdf |
| Texte | .doc, .docx, .odt, .rtf, .txt, .pages |
| Tableurs | .xls, .xlsx, .ods, .numbers, .csv |
| Présentations | .ppt, .pptx, .odp, .key |
| Images | .jpg, .jpeg, .png, .gif, .bmp, .tiff, .heic, .webp, .svg |
| Vidéos | .mp4, .mov, .avi, .mkv, .m4v, .wmv |
| Audio | .mp3, .m4a, .wav, .aac, .flac, .ogg |
| Archives | .zip, .tar, .gz, .rar, .7z |
| Code | .py, .js, .ts, .html, .css, .json, .xml, .yaml, .sh, .swift… |
| Autres | Tout le reste |

---

# Fonds de manuscrits — `export_photos_album.py`

Second script du dépôt : exporte un **album iCloud Photos** vers un dossier
local, pour alimenter le traitement documentaire décrit dans
[`manuscrits/README.md`](manuscrits/README.md).

```bash
# Lister les albums
python export_photos_album.py --username votre@apple.com --list-albums

# Exporter un album, avec conversion HEIC → JPEG (macOS)
python export_photos_album.py -u votre@apple.com -a "Manuscrits" \
    -o ~/Desktop/Manuscrits --jpeg
```

> À exécuter sur votre machine. Ne saisissez jamais votre mot de passe Apple
> dans une session distante.

Sans passer par le script, l'export manuel depuis Photos.app fait aussi
l'affaire : sélectionner l'album → *Fichier > Exporter > Exporter N photos* →
JPEG, qualité maximale, taille pleine.
