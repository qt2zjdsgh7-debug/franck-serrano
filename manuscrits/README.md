# Fonds de manuscrits et lettres autographes — protocole de traitement

Ce dossier organise le traitement d'un fonds de documents manuscrits :
numérisation, transcription, fiches produits, rapport de classement.

## Arborescence

```
manuscrits/
├── 01_sources/     Photographies des documents (JPEG)
├── 02_fiches/      Une fiche produit par document (Markdown)
├── 03_rapport/     Rapport de synthèse et classement
├── MODELE_FICHE.md Gabarit de fiche produit
└── INVENTAIRE.csv  Table de bord de l'ensemble du fonds
```

## 1. Prise de vue

La qualité de la photo détermine la qualité de la transcription. Une écriture
du XIXe siècle mal éclairée est illisible, même pour un œil humain.

- **Lumière naturelle diffuse**, jamais de flash (l'encre ferro-gallique se
  noie dans le reflet). Près d'une fenêtre, sans soleil direct.
- **Appareil parallèle à la feuille**, page entière dans le cadre, sur fond
  uni sombre. Éviter l'ombre portée du téléphone.
- **Une photo par face**, y compris les versos apparemment vierges
  (annotations, cachets, filigranes s'y trouvent souvent).
- **Photographier aussi** : l'enveloppe recto/verso, les cachets de cire, les
  timbres et oblitérations, les marques de collection, les filigranes
  (en contre-jour), les chemises ou notes d'archivage anciennes.
- **Un repère d'échelle** (règle, pièce de monnaie) sur au moins une photo
  par document.
- **Détail rapproché** des passages clés ou d'une signature difficile.
- Résolution minimale ~8 Mpx. Ne pas recadrer agressivement : les bords
  du papier renseignent sur le format et l'état.

## 2. Format et nommage

**Format : JPEG.** Le HEIC d'Apple n'est pas exploitable directement.
Conversion sur Mac, en une ligne :

```bash
cd ~/Desktop/ExportPhotos
mkdir -p jpeg && sips -s format jpeg -s formatOptions 90 *.HEIC --out jpeg/
```

**Nommage** — un identifiant par document, un suffixe par vue :

```
DOC-001_f01r.jpg      feuillet 1 recto
DOC-001_f01v.jpg      feuillet 1 verso
DOC-001_f02r.jpg      feuillet 2 recto
DOC-001_env-r.jpg     enveloppe recto
DOC-001_env-v.jpg     enveloppe verso
DOC-001_detail-01.jpg détail (signature, cachet, filigrane)
DOC-002_f01r.jpg      document suivant
```

Si le nommage est trop fastidieux, envoyez les photos en vrac dans l'ordre :
je les renomme et je reconstitue les groupes, en vous soumettant le
regroupement pour validation avant d'aller plus loin.

## 3. Transmission

**Voie A — pièces jointes dans la conversation** (la plus simple)
Vous joignez les photos directement à un message. Par lots de 20 à 30 vues
pour que je garde assez de mémoire de travail pour transcrire finement.
Aucun identifiant à communiquer.

**Voie B — dépôt dans ce repo** (recommandée pour un fonds volumineux)
Vous déposez les JPEG dans `manuscrits/01_sources/` et poussez sur la
branche. Je les lis depuis le disque. Avantages : l'ensemble reste versionné,
les fiches et le rapport vivent à côté des sources, et le travail est
reprenable d'une session à l'autre.

Depuis un Mac, une fois l'album exporté :

```bash
cp ~/Desktop/ExportPhotos/jpeg/*.jpg manuscrits/01_sources/
git add manuscrits/01_sources && git commit -m "Ajout lot 1" && git push
```

> **Sécurité.** Ne saisissez jamais votre mot de passe Apple dans une session
> cloud. Les scripts qui touchent à iCloud s'exécutent sur votre machine,
> jamais ici.

## 4. Export de l'album depuis Apple Photos

**Méthode recommandée, sans code** — Photos.app sur Mac :
sélectionner l'album → *Fichier > Exporter > Exporter N photos* →
format JPEG, qualité maximale, taille : pleine → choisir un dossier.

**Méthode scriptée** — `export_photos_album.py` à la racine du repo, à lancer
sur votre Mac (voir son en-tête). Utile pour des exports répétés.

## 5. Ce que je produis

1. **Une fiche produit par document** dans `02_fiches/`, selon
   `MODELE_FICHE.md` : identification, description matérielle, état,
   transcription, intérêt historique, provenance, évaluation commerciale.
2. **`INVENTAIRE.csv`** : table de bord de l'ensemble, triable.
3. **Un rapport de classement** dans `03_rapport/` : double hiérarchie
   commerciale et historique, lots de vente suggérés, recommandations
   de valorisation (vente, conservation, publication, dépôt institutionnel).

## 6. Réserves méthodologiques

- Une transcription faite sur photographie reste une **lecture proposée**.
  Les passages incertains sont signalés `[?]`, les illisibles `[…]`.
- Les **attributions** (auteur, date, destinataire) non signées sont données
  comme hypothèses argumentées, jamais comme des faits établis.
- Les **estimations** sont des ordres de grandeur fondés sur des comparables
  publics, à confronter à une expertise en main propre. Aucune photographie
  ne remplace l'examen du papier, des filigranes et de l'encre.
- L'**authentification** d'un autographe de valeur relève d'un expert
  assermenté. Mon travail prépare et documente ce passage, il ne s'y substitue pas.
