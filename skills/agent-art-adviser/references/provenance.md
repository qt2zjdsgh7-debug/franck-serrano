# Analyse de provenance et conformité — agent-art-adviser

Méthode, bases et signaux d'alerte. Les entrées marquées ✓ ont été vérifiées en ligne à la date indiquée ; les autres sont des repères à confirmer avant citation. Les règles juridiques (seuils d'exportation, anti-blanchiment, listes de sanctions) changent : vérifier à chaque commande et renvoyer vers un conseil.

Dernière révision : 2026-10-19

---

## 1. Format normalisé d'une provenance

Convention la plus lue (musées américains, grandes maisons) : un maillon par ligne, du plus ancien au plus récent ; **point-virgule** quand le passage d'un propriétaire au suivant est direct, **point** quand il y a une rupture ou une incertitude ; les ventes entre crochets ou en italique ; les mentions « probablement », « peut-être » assumées.

```
L'artiste, Paris ; vendu à
Galerie X, Paris, 1931 (stock n° 1234) ; vendu à
M. Y, Lyon, 1933 ; par descendance à
Mme Z, Genève.
[Vente, Hôtel Drouot, Paris, 12 mars 1978, lot 45] ; acquis par
Collection privée, Suisse ; par descendance au propriétaire actuel.
```

Dans le dossier Aion, le tableau de travail ajoute pour chaque maillon :

| Colonne | Contenu |
|---|---|
| Propriétaire | Nom, lieu, dates de vie ou d'activité ; forme en FR / EN / ZH si pertinent |
| Dates de détention | De … à … ; « avant », « après », « vers » si incertain |
| Mode d'acquisition | Achat, don, héritage, échange, dation, saisie, vente forcée, restitution |
| Preuve | Facture, lettre, livre de stock, catalogue de vente, étiquette, cachet, photo d'archive, catalogue d'exposition, mention dans le catalogue raisonné |
| Niveau | A (document vu) / B (notice ou source secondaire) / C (allégué) |
| Remarque | Écart, contradiction, question à poser |

Un maillon C est un trou. Les trous se listent à part, avec les dates qu'ils couvrent.

## 2. Périodes sensibles

| Période | Zone | Risque |
|---|---|---|
| 1933-1945 | Allemagne, Autriche, pays occupés, France de Vichy | Spoliations nazies, ventes forcées, « aryanisations », ventes sous contrainte à l'étranger par des émigrés. Les Principes de Washington (1998) et la déclaration de Terezín (2009) fondent la pratique des musées et des maisons. |
| 1917-1930 | Russie, URSS | Nationalisations et ventes soviétiques. |
| 1936-1939 | Espagne | Guerre civile, dispersions. |
| 1937-1945 | Chine occupée, Asie du Sud-Est, Corée | Pillages japonais, dispersions, collections de Shanghai et de Pékin déplacées. |
| 1949 | Chine | Exode vers Taïwan, Hong Kong, les États-Unis ; collections sorties ou confisquées. |
| 1966-1976 | Chine | Révolution culturelle : confiscations (抄家), destructions, restitutions partielles dans les années 1980 ; une œuvre « redécouverte » sans trace entre 1966 et 1980 doit être expliquée. |
| Depuis 1970 | Tous pays | Convention UNESCO 1970 sur les biens culturels ; pillage archéologique (hors périmètre art moderne, mais pertinent pour les antiquités chinoises). |
| 1990-2000 | Ex-Yougoslavie, Irak, Afghanistan | Conflits et pillages. |
| Depuis 2014 et 2022 | Russie, Ukraine | Sanctions internationales : vendeur ou acheteur sous sanction, œuvre déplacée depuis les zones occupées. |

## 3. Bases d'œuvres spoliées, volées ou disparues

| Base | Institution | Périmètre | Accès |
|---|---|---|---|
| **Getty Provenance Index** | Getty Research Institute | Livres de stock de marchands (Goupil, Knoedler, Duveen…), catalogues de vente anciens, inventaires d'archives ; nouvelle plateforme **Arches** en données ouvertes depuis le **1er mai 2025** (livres de stock et catalogues de vente ; inventaires à suivre) ; l'ancienne plateforme reste en parallèle ✓ | Gratuit |
| **Lost Art-Datenbank** (lostart.de) | Deutsches Zentrum Kulturgutverluste | Œuvres spoliées ou disparues, Allemagne et pays occupés ; déclarations de recherche et de perte | Gratuit |
| **ERR Project** (errproject.org) | Conference on Jewish Material Claims / US Holocaust Memorial Museum | Fiches de l'Einsatzstab Reichsleiter Rosenberg, Jeu de Paume, collections françaises et belges saisies | Gratuit |
| **Commission for Looted Art in Europe** (lootedart.com) | CLAE | Portail central, législations, affaires | Gratuit |
| **Base Rose-Valland / MNR** (pop.culture.gouv.fr) | Ministère de la Culture (France) | Œuvres « Musées nationaux récupération » en attente de restitution ; dossiers de la Commission de récupération artistique | Gratuit |
| **CIVS** | Commission pour l'indemnisation des victimes de spoliations (France) | Réclamations, recommandations | Site |
| **Munich Central Collecting Point / Property Cards** | Deutsches Historisches Museum, NARA (Fold3) | Fiches des œuvres passées par les points de collecte alliés | Gratuit |
| **Art Loss Register** | Société privée (Londres) | Plus grande base d'œuvres volées et contestées ; **certificat de recherche** exigé par les maisons et les assureurs | Payant, par requête |
| **Interpol — Stolen Works of Art** et application **ID-Art** | Interpol | Œuvres volées signalées par les polices | Gratuit sur inscription |
| **ICOM Red Lists** | Conseil international des musées | Catégories d'objets à risque par pays | Gratuit |
| **Spoliation Advisory Panel** (Royaume-Uni), **Restitutiecommissie** (Pays-Bas), **Kommission für Provenienzforschung** (Autriche), **Beratende Kommission** (Allemagne) | Commissions nationales | Décisions publiées : utiles pour la jurisprudence | Gratuit |
| **NEPIP** (Nazi-Era Provenance Internet Portal) | AAM (États-Unis) | Œuvres de musées américains à provenance lacunaire 1933-1945 | Gratuit |
| **FBI National Stolen Art File** | FBI | Œuvres volées aux États-Unis | Gratuit |
| **国家文物局 — 被盗文物信息发布平台** | Administration nationale du patrimoine (Chine) | Biens culturels volés déclarés en Chine | Gratuit, en chinois |

Chaque interrogation est consignée : base, critères, date, résultat, référence du certificat. Une interrogation de plus de six mois est refaite avant toute transaction.

## 4. Archives de marchands, de collectionneurs et de ventes

| Fonds | Lieu | Usage |
|---|---|---|
| Knoedler, Goupil, Duveen, Jacques Seligmann (partiel) | Getty Research Institute (livres de stock dans le Provenance Index) ; Archives of American Art pour Seligmann | Passages par le marché new-yorkais et parisien, XIXe-XXe |
| Wildenstein Plattner Institute | New York | Archives Wildenstein, Paul Rosenberg (partiel), catalogues numériques |
| Zentralarchiv — Staatliche Museen zu Berlin | Berlin | Archives de galeries et de marchands allemands (Cassirer, Flechtheim, Thannhauser selon fonds) |
| Bibliothèque Kandinsky — Centre Pompidou | Paris | Fonds de galeries et de critiques ; archives d'expositions (voir agent-historien) |
| INHA — Bibliothèque | Paris | Catalogues de vente annotés (XVIIIe-XXe), fonds de marchands |
| Fondation Custodia — **Lugt**, *Les Marques de collections* (marquesdecollections.fr) | Paris | Identification des cachets et marques de collection, de vente et d'atelier ; indispensable pour les dessins et estampes |
| Archives des maisons de ventes | Christie's, Sotheby's (archives internes sur demande, partiellement en ligne) ; Drouot (catalogues anciens à l'INHA, Gallica) | Retrouver un passage en vente et son acheteur |
| RKD | La Haye | Documentation d'artistes et d'images, provenance néerlandaise |
| Frick Art Reference Library | New York | Catalogues de vente, photographies d'archives |
| Asia Art Archive | Hong Kong | Art chinois depuis les années 1980, archives de galeries |
| Archives des galeries | Galerie de l'artiste, successions de galeristes | Livres de stock et factures : la source A par excellence pour un artiste du XXe |

## 5. Indices matériels à lire au dos de l'œuvre

- **Étiquettes d'exposition** : institution, titre, numéro de prêt ; à confronter au catalogue de l'exposition (agent-historien).
- **Étiquettes et cachets de galerie** : numéro de stock, à retrouver dans les archives de la galerie.
- **Cachets de collection et de vente** : Lugt.
- **Cachets d'atelier** (vente d'atelier après décès) : indiquent souvent un passage par une vente de succession datée.
- **Numéros d'inventaire** au pochoir ou au crayon : douane, dépôt, collection ; les numéros du type « MNR » ou des points de collecte alliés sont des alertes à traiter d'abord.
- **Étiquettes de transporteurs et de douane** : datent les déplacements.
- **Châssis, toile, rentoilage, encadrement** : cohérence avec la date et le lieu allégués.

Photographier le dos en entier et chaque étiquette ; ne jamais retirer une étiquette.

## 6. Signaux d'alerte et grille de risque

**Rouge (bloquant tant que non levé)**
- Trou couvrant une période sensible sans explication documentée
- Correspondance avec une déclaration dans Lost Art, ERR, Art Loss Register, Interpol, MNR
- Vendeur ou bénéficiaire effectif sous sanction, ou impossible à identifier
- Œuvre soumise à une interdiction d'exportation dans son pays d'origine et présentée hors de ce pays sans autorisation
- Certificat ou numéro de catalogue dont la vérification échoue

**Orange (à lever avant la transaction)**
- Provenance uniquement déclarative (« collection privée, Europe ») sur plus d'un maillon
- Certificat d'un tiers non reconnu
- Écarts entre la notice du catalogue raisonné et l'œuvre
- Passages répétés en vente, invendus successifs
- Pression sur le calendrier, paiement vers un tiers, refus d'inspection

**Vert (à documenter)**
- Chaîne continue, chaque maillon de niveau A ou B
- Œuvre exposée ou publiée du vivant de l'artiste
- Interrogations des bases négatives et datées
- Titre de propriété et pièces d'importation disponibles

La grille finale du rapport donne une couleur par axe : catalogue raisonné / provenance / état / marché / juridique.

## 7. Exportation, importation, restrictions

| Zone | Règle (à confirmer à chaque commande) |
|---|---|
| **France** | Certificat d'exportation pour les biens culturels dépassant des seuils d'âge et de valeur fixés par catégorie (par exemple tableaux de plus de 50 ans au-dessus d'un seuil de valeur ; dessins, estampes, sculptures à leurs propres seuils) ; possibilité de refus de certificat (« trésor national ») suivi d'une offre d'achat de l'État sous 30 mois ; licence d'exportation UE en plus du certificat pour une sortie hors Union. Seuils à vérifier sur le site du ministère de la Culture. |
| **Union européenne** | Règlement sur l'exportation des biens culturels (licence) et règlement 2019/880 sur l'importation des biens culturels (licence ou déclaration à l'importation pour certains biens de pays tiers, applicable progressivement). |
| **Royaume-Uni** | Licence d'exportation Arts Council ; critères Waverley ; régime post-Brexit distinct de l'UE. |
| **Suisse** | Loi sur le transfert des biens culturels (LTBC) ; ports francs (Genève) : la localisation en port franc n'est pas une preuve de légalité. |
| **États-Unis** | Pas de contrôle général à l'exportation d'art moderne ; CBP à l'importation ; sanctions OFAC ; antiquités soumises depuis 2021 au Bank Secrecy Act. |
| **Chine continentale** | Loi sur la protection des biens culturels (révisée en 2024, en vigueur le 1er mars 2025 : à confirmer) ; **avis de l'Administration nationale du patrimoine du 26 mai 2023** ✓ : liste des artistes morts après 1911 dont les œuvres sont restreintes à l'exportation en 8 catégories ; pour la peinture et la calligraphie, **41 artistes dont toutes les œuvres sont interdites de sortie** (dont Qi Baishi, Xu Beihong, Lin Fengmian, Wu Guanzhong, Zhang Daqian, Fu Baoshi, Huang Binhong, Li Keran, Wu Changshuo, Liu Haisu, Chen Yifei, Feng Zikai, Guan Shanyue) et **158 artistes dont les œuvres représentatives sont interdites** ; les listes de 2001 et 2013 sont abrogées. Vérification à l'exportation par les services du patrimoine (文物进出境审核). À l'importation : droits de douane et TVA ; les zones franches (Shanghai, Pékin) servent au stockage et à l'exposition temporaire. |
| **Hong Kong** | Port franc, pas de droits ni de TVA sur les œuvres ; c'est l'une des raisons de sa place dans les ventes. |
| **Taïwan** | Loi sur la préservation du patrimoine culturel pour les biens classés ; art moderne généralement libre. |

## 8. Anti-blanchiment, sanctions, identification

- **Union européenne** : 5e directive anti-blanchiment (2018), transposée au plus tard le **10 janvier 2020** ✓ ; les marchands, intermédiaires, maisons de ventes et exploitants de ports francs sont assujettis pour toute transaction ou série de transactions liées à partir de **10 000 €** : identification du client et du bénéficiaire effectif, évaluation des risques, conservation des pièces, déclaration de soupçon. Le paquet AML européen de 2024 (règlement unique, autorité AMLA) prolonge ce régime : vérifier l'état d'application.
- **France** : transposition dans le Code monétaire et financier ; déclaration à Tracfin ; obligations des opérateurs de ventes volontaires et des antiquaires.
- **Royaume-Uni** : *Art Market Participants* enregistrés auprès de HMRC, même seuil de 10 000 € (environ 8 600 £) ✓ ; amendes appliquées depuis 2022 ✓ ; obligations distinctes sous le Proceeds of Crime Act.
- **États-Unis** : pas d'obligation AML fédérale générale pour les marchands d'art moderne à la date de révision (antiquités : oui) ; sanctions **OFAC** applicables à toute personne américaine et aux paiements en dollars.
- **Chine** : contrôle des changes (SAFE) sur les paiements vers l'étranger ; les paiements fractionnés ou via des tiers sont des signaux d'alerte.
- **Pratique Aion** : identifier le bénéficiaire effectif des deux côtés ; refuser un paiement émanant d'un tiers non identifié ; consulter les listes de sanctions UE, OFAC et UK avant tout engagement ; conserver les pièces dix ans.

## 9. Jurisprudence et affaires à connaître (pour lire une provenance)

- **Knoedler / Rosales** (New York, 2011-2016) : provenance inventée (« Mr. X », collectionneur suisse anonyme) pour des faux d'expressionnistes abstraits ; leçon : une provenance anonyme répétée est une alerte, même chez un marchand prestigieux.
- **Beltracchi** (Allemagne, 2010-2011) : collection « Jägers » fabriquée avec de fausses étiquettes de galerie Flechtheim ; leçon : vérifier les étiquettes dans les archives de la galerie, pas seulement leur aspect.
- **Gurlitt** (Munich, 2012-2014) : collection d'un marchand du IIIe Reich ; leçon : les listes Lost Art et le travail de la Taskforce Schwabinger Kunstfund.
- **Affaires Modigliani** (Gênes 2017, saisies) : absence d'autorité unique ; leçon : pour certains artistes, la provenance fait toute la valeur.
- **Faux Lin Fengmian et Qi Baishi** : nombre de faux en circulation très élevé ; leçon : une provenance d'exposition du vivant de l'artiste ou un passage par une collection documentée (famille, élève, musée) vaut plus qu'un certificat.
- **Affaires de non-règlement en Chine** (Qi Baishi 2011, 《松柏高立图》 adjugé 425 millions de RMB non réglé) : leçon : adjugé n'est pas payé.

## 10. Procédure type d'analyse de provenance

1. Rassembler ce que fournit le vendeur et le reformuler au format normalisé, en marquant chaque maillon C.
2. Lire le dos de l'œuvre (photos) : étiquettes, cachets, numéros ; identifier via Lugt et les archives de galeries.
3. Confronter avec le catalogue raisonné (provenance et expositions listées), les catalogues d'exposition et la bibliographie.
4. Chercher les passages en vente : bases agrégées, archives des maisons, Getty Provenance Index pour les périodes anciennes, Drouot/INHA pour Paris.
5. Couvrir chaque période sensible : qui détenait l'œuvre, où, avec quelle preuve ; si la réponse est « on ne sait pas », l'écrire.
6. Interroger les bases d'œuvres spoliées ou volées (§ 3) et consigner chaque interrogation.
7. Vérifier la situation du vendeur (identité, bénéficiaire effectif, sanctions) et la situation d'exportation de l'œuvre (§ 7).
8. Rédiger le tableau, la liste des trous, les demandes au vendeur, la grille de risque, et transmettre à agent-contrats les garanties contractuelles à prévoir (garantie de titre, de provenance, clause de restitution, indemnisation).
