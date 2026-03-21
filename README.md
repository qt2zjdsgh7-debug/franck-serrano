# Téléchargement et organisation iCloud Drive

Script Python pour télécharger tous les documents d'un compte iCloud et les organiser automatiquement en dossiers et sous-dossiers.

## Structure des dossiers créés

```
iCloud_Documents/
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
iCloud_Documents/
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
# Téléchargement de base
python download_icloud.py --username votre@apple.com

# Avec organisation par année
python download_icloud.py --username votre@apple.com --by-year

# Dossier de destination personnalisé
python download_icloud.py --username votre@apple.com --output ~/Bureau/MesDocuments

# Toutes les options
python download_icloud.py \
    --username votre@apple.com \
    --password "motdepasse" \
    --output ~/iCloud_Backup \
    --by-year \
    --verbose
```

## Options

| Option | Description |
|--------|-------------|
| `--username` / `-u` | Identifiant Apple (obligatoire) |
| `--password` / `-p` | Mot de passe Apple (demandé si absent) |
| `--output` / `-o` | Dossier de destination (défaut: `~/iCloud_Backup`) |
| `--by-year` | Créer un sous-dossier par année de modification |
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
