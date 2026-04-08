# Téléchargement et organisation iCloud Drive par chantier

Script Python qui :
1. **Télécharge** tous les documents de votre iCloud Drive en local
2. **Crée automatiquement** les dossiers organisés **par chantier/projet puis par type** directement dans iCloud Drive

Après exécution, ouvrez l'app **Fichiers** sur iPhone/iPad ou le Finder sur Mac → **iCloud Drive** → `Documents_Organisés/`

> **Note :** Seuls les fichiers iCloud Drive sont accessibles via ce script. Les fichiers stockés **uniquement en local sur l'iPad** (hors iCloud) ne peuvent pas être organisés automatiquement.

## Structure des dossiers créés

```
Documents_Organisés/
├── Renovation_Cuisine/        ← nom du dossier d'origine dans iCloud
│   ├── PDF/
│   │   └── devis.pdf
│   ├── Images/
│   │   └── photo_avant.heic
│   └── Tableurs/
│       └── budget.xlsx
├── Chantier_Dupont/
│   ├── PDF/
│   │   └── contrat.pdf
│   └── Texte/
│       └── notes.docx
└── Sans_Projet/               ← fichiers sans dossier parent dans iCloud
    └── PDF/
        └── document.pdf
```

### Règle de classement

Le **nom du chantier** est déterminé par le **dossier de premier niveau** dans iCloud Drive où se trouve le fichier.

- `Renovation_Cuisine/Devis/devis.pdf` → rangé dans `Renovation_Cuisine/PDF/`
- `Chantier_Dupont/contrat.pdf` → rangé dans `Chantier_Dupont/PDF/`
- `document.pdf` (à la racine) → rangé dans `Sans_Projet/PDF/`

### Option `--by-year`

Un sous-dossier par année est ajouté entre le type et le fichier :

```
Documents_Organisés/
└── Renovation_Cuisine/
    └── PDF/
        ├── 2024/
        │   └── devis.pdf
        └── 2025/
            └── facture_finale.pdf
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
