# Téléchargement et organisation iCloud Drive

Script Python qui :
1. **Télécharge** tous les documents de votre iCloud Drive en local
2. **Crée automatiquement** les dossiers organisés **par thème puis par type** directement dans iCloud Drive

Après exécution, ouvrez l'app **Fichiers** sur iPhone/iPad ou le Finder sur Mac → **iCloud Drive** → `Documents_Organisés/`

## Structure des dossiers créés

```
Documents_Organisés/
├── Travail/
│   ├── PDF/
│   │   └── contrat.pdf
│   ├── Texte/
│   │   └── rapport.docx
│   ├── Présentations/
│   │   └── slides.key
│   └── Code/
│       └── script.py
├── Personnel/
│   ├── Texte/
│   │   └── note.txt
│   └── Archives/
│       └── backup.zip
├── Finances/
│   └── Tableurs/
│       └── budget.xlsx
└── Médias/
    ├── Images/
    │   └── photo.heic
    ├── Vidéos/
    │   └── film.mov
    └── Audio/
        └── musique.m4a
```

### Détection du thème

Le thème est déterminé **en deux étapes** :

1. **Mots-clés dans le chemin iCloud** — si le fichier se trouve dans un dossier contenant un mot reconnu, il est classé dans le thème correspondant :

| Thème | Mots-clés détectés |
|-------|-------------------|
| Travail | travail, pro, boulot, professionnel, job, office, bureau, contrat, client |
| Finances | facture, finance, banque, compta, impôt, fiscal, budget… |
| Médias | photo, vidéo, image, média, musique, souvenir… |
| Personnel | personnel, perso, famille, privé, maison, santé… |

2. **Fallback par type de fichier** — si aucun mot-clé n'est trouvé :

| Type | Thème par défaut |
|------|-----------------|
| Images, Vidéos, Audio | Médias |
| Tableurs | Finances |
| PDF, Texte, Présentations, Code | Travail |
| Archives, Autres | Personnel |

### Option `--by-year`

Un sous-dossier par année est ajouté entre le type et le fichier :

```
Documents_Organisés/
├── Travail/
│   └── PDF/
│       ├── 2023/
│       │   └── contrat.pdf
│       └── 2024/
│           └── facture.pdf
└── Médias/
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
