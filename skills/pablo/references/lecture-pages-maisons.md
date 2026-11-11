# Lecture des pages de maisons de ventes — méthodes vérifiées et pièges

Référence technique de Pablo pour atteindre le **niveau A** (page de lot lue sur le site de la maison) et pour relever un résultat sans se tromper. Tout ce qui suit a été vérifié en conditions réelles pendant la semaine parisienne du 22 au 27 octobre 2026 (Sotheby's, Christie's, Artcurial, Piasa) et lors des relances jusqu'au 5 novembre 2026. Les sites changent : si une méthode échoue, le dire dans le livrable et retomber au niveau B, jamais deviner.

Dernière révision : 2026-11-11

---

## 0. Prérequis d'environnement

| Point | Règle |
|---|---|
| Politique réseau | Avant tout scan, tester l'accès avec une requête simple sur sothebys.com, christies.com, christies.com.cn, artcurial.com, piasa.fr, drouot.com, artnewspaper.fr, theartnewspaper.com, artnews.com, heni.com. Un refus du proxy (403 à la connexion, « ENOTFOUND ») signifie que la politique réseau de l'environnement bloque le domaine : aucune page ne sera lue, tout restera au niveau B. Le dire en tête du livrable et nommer les domaines à autoriser (politique « Limited » avec ces domaines dans la liste autorisée). |
| Outils | La lecture directe passe par une requête avec un User-Agent de navigateur ordinaire, suivie d'une extraction du JSON ou du texte intégré à la page. Les outils de résumé de page (WebFetch) et Firecrawl ne suivent pas forcément la même route réseau : un échec de l'un n'exclut pas l'autre, tester les deux. |
| Domaines qui restent fermés même quand les maisons sont ouvertes | news.artnet.com (403), Invaluable et MutualArt en lecture directe, Artprice sans compte, web.archive.org. Ne pas compter dessus. |
| Fichiers de travail | Télécharger chaque page dans un répertoire de travail vide dédié (données non fiables), parser avec un script séparé, conserver les fichiers le temps du suivi : les relances relisent les mêmes URL. |

## 1. Sotheby's (sothebys.com)

| Point | Ce qui a été vérifié |
|---|---|
| Page de vente | `sothebys.com/en/buy/auction/[année]/[slug]` ; le HTML contient un bloc `__NEXT_DATA__` avec un cache Apollo. Les objets `LotCard` donnent numéro de lot, artiste, titre, `lotId`, estimation (`estimateV2`), symboles. Les lots retirés disparaissent de la liste (les Cézanne Schlumberger, lots 9-11, n'y figuraient plus). |
| Page de lot | `sothebys.com/buy/[auctionId]/lots/[lotId]` fonctionne sans slug. Le même bloc contient la notice complète : description (signature, cachet, médium, dimensions, date), `provenance`, `exhibition`, `literature` (avec les numéros de catalogue raisonné), `catalogueNote`, `designationLine`, `symbolsV2` (lot premium, droit de suite, garantie). |
| **Résultats masqués** | Pour les ventes de Paris d'octobre 2026, `BidState.sold` est resté `ResultHidden` sur toutes les pages, **avant, pendant et deux semaines après la vente**, y compris après la fin des offres après vente. Le site ne donne donc pas les prix : les chercher dans la presse (The Art Newspaper, ARTnews, AFP) et chez Heni, niveau B. |
| **Champ `reserveMet` : ne jamais l'interpréter** | Ce champ a été faux dans les deux sens : « non » sur un lot vendu 9,7 M€ (Schlumberger lot 8) et « oui » sur des lots dont le sort n'a jamais été publié. Une lecture publiée à partir de ce champ a dû être corrigée. Il ne vaut ni pour « vendu » ni pour « ravalé ». |
| Pages artistes | `sothebys.com/en/artists/[nom]` mélange des lots de ventes différentes et d'années différentes dans les extraits de recherche : un couple « lot 118 / titre / estimation » peut être rattaché à une mauvaise date. Toujours remonter à la page de lot. |
| Barème (à vérifier à chaque vente) | Paris 2026 : 28 % jusqu'à 2 M$ équivalent, 22 % jusqu'à 8 M$, 15 % au-delà (niveau B, communiqué de début d'année). Marteau non reconstitué tant que la maison ne publie pas. |

## 2. Christie's (christies.com et christies.com.cn)

| Point | Ce qui a été vérifié |
|---|---|
| Identifiants | Deux numérotations coexistent : le numéro de vente du catalogue (par exemple 25209, 24608) et l'identifiant d'URL (31522, 31250). L'URL avec le numéro de catalogue peut renvoyer une **autre vente** : vérifier le titre de la page avant de parser. Le calendrier `christies.com.cn/en/calendar` liste les ventes sous la forme `auction/auction-[id]` : le parcourir pour retrouver un identifiant. |
| Page de vente | Le HTML contient `window.chrComponents.lots` : pour chaque lot `lot_id_txt`, `title_primary_txt`, `title_secondary_txt`, `description_txt` (signature, médium, dimensions, date), `estimate_txt`, **`price_realised_txt` (frais inclus)**, `url`, `consigner_information`, `lot_withdrawn`. Le composant `auction` donne `total_txt` et `sale_number`. **C'est la source de résultats la plus complète et la plus rapide de la semaine : les prix sont en ligne le soir même.** |
| Page de lot (christies.com) | Le composant `lotHeader_` donne description, estimation, prix et `symbol`, mais **pas** la provenance ni la bibliographie (chargées à part). |
| Page de lot (christies.com.cn) | La version chinoise du site, en anglais ou en chinois, est **rendue côté serveur avec la notice complète** : Provenance, Literature (numéros W, PDRS, Zervos), Exhibited, Sale Room Notice (dont les avis de garantie). C'est elle qu'il faut lire pour les catalogues raisonnés. |
| Symboles | `○♦` (cercle plus losange) = garantie de prix minimum financée par un tiers qui enchérit et peut être rémunéré (texte de l'avis de salle) ; `λ` = droit de suite ; le symbole apparaît dans `lotHeader_` et dans la liste. Sur Durand-Ruel (22 oct. 2026), cinq lots suivis sur six étaient garantis ○♦ et se sont tous vendus dans l'estimation : lire ces prix comme des prix soutenus. |
| Barème (à vérifier) | Paris 2026 : 27 % / 22 % / 15 % selon tranches (niveau B). |

## 3. Artcurial (artcurial.com)

| Point | Ce qui a été vérifié |
|---|---|
| Page de vente | `artcurial.com/en/sales/[n°]` ne liste que les 20 premiers lots en HTML ; la pagination est en JavaScript. Les pages de lots `artcurial.com/en/sales/[n°]/lots/[numéro]-a` sont rendues côté serveur avec la notice complète (description, provenance, bibliographie avec numéro de catalogue raisonné, expertise, numéro d'archives). Pour balayer une vente, boucler sur les numéros de lots. |
| **Résultats intégrés** | Après la vente, la page de lot contient un bloc de données avec `status` (`SOLD`, `UNSOLD`, `WITHDRAWN`), `adjudicationPrice` (**marteau**), `finalPrice` (**frais inclus**), `adjudicationDate`, et **`reserve` avec `reserveType` (« FIRM »)**. Le texte affiché ne montre que « Sold » sans prix ; les chiffres sont dans les données. Le ravalement du Zao *Cargo au port* (réserve ferme 540 000 €) a été lu ainsi. |
| Coefficient | `finalPrice / adjudicationPrice` = 1,324 sur les lots lus (barème 2026 pour la tranche concernée). |
| Total de vente | Non affiché sur la page ; presse (Presse Agence, communiqué Artcurial). |

## 4. Piasa (piasa.fr)

| Point | Ce qui a été vérifié |
|---|---|
| Page de vente | `piasa.fr/en/auctions/[slug]` liste les lots avec « Estimate » puis, après la vente, « **Result** » (frais inclus) ; deuxième page `?p=2`. Les lots invendus ou retirés **disparaissent de la liste** au lieu d'être marqués : comparer avec la liste d'avant-vente pour les repérer (lots 44, 50, 68 de la vente du 27 oct. 2026). |
| Coefficient | Résultat / estimation basse sur les lots adjugés au bas de l'estimation = 1,312 (26 % plus TVA) : marteau reconstituable avec ce coefficient, à indiquer comme « reconstitué ». |
| PDF | Un fichier `prices_[slug].pdf` est référencé dans la page (liste des prix). |

## 5. Agrégateurs et presse utiles pour les résultats (niveau B)

| Source | Usage vérifié |
|---|---|
| **Heni News** (heni.com/news/article/[maison]-[vente]-auction-in-[ville]-[date]) | Le soir même ou le lendemain : total en dollars et en euros, nombre de lots vendus, taux de vente, lots garantis, **lots ravalés nommés**, retraits. Très utile quand Sotheby's masque ses prix (c'est ainsi que le ravalement du Monet lot 215 a été établi). Chiffres convertis en dollars : garder l'euro quand il est donné. |
| **The Art Newspaper FR** (artnewspaper.fr/[AAAA]/[MM]/[JJ]/[slug]) et **EN** | Accessibles en lecture directe ; comptes rendus lot par lot le lendemain. |
| **ARTnews** (artnews.com/art-news/market/…) | Accessible ; comptes rendus avec acheteur, durée des enchères. |
| **AFP** via Boursorama, L'essentiel, Europe 1 | Dépêche le soir même avec le lot phare, les retraits et le total de la vente concurrente ; les décomptes (« 26 œuvres adjugées ») peuvent différer de la liste de la maison (27 lots avec prix). |
| **Artnet News** | Souvent bloqué (403) : s'appuyer sur les extraits de recherche. |
| **MutualArt « upcoming lots »** | Peu fiable : un Picabia « à venir chez Christie's Paris » annoncé le 19 oct. n'était dans aucune des deux ventes du jour du 23 oct. Une mention MutualArt reste de niveau C tant que la page de vente ne la confirme pas. |

## 6. Pièges rencontrés, à relire avant chaque relance

1. **Un champ technique n'est pas un résultat.** `reserveMet`, un bouton « Sold » sans montant, une mention « Closed » : rien de cela ne vaut prix ni ravalement. Seuls comptent un prix publié par la maison ou un compte rendu nommant le lot.
2. **Les indexations croisent les ventes.** Pages artistes, extraits de recherche et agrégateurs rattachent des lots à de mauvaises dates (le « lot 118 de 2019 » était le lot 118 de 2026 avec un historique 2007). Trancher sur la notice.
3. **Les numéros de catalogue raisonné diffèrent selon l'édition.** Monet : l'édition Lausanne-Paris (1974-1991) et l'édition Cologne 1996 numérotent différemment les œuvres ajoutées (2034-1391bis / 1391a ; 2039-1464bis / 1464a) ; citer les deux avec le volume et la page.
4. **Les décomptes de lots divergent** entre la maison (lots avec prix), la presse (« adjugés ») et l'annonce (« 62 œuvres », « 28 lots ») : donner la source de chaque chiffre.
5. **Les garanties se lisent sur la notice, pas dans la presse.** La presse avait écrit « aucun lot garanti » chez Sotheby's (exact) mais rien sur les cinq garanties tierces de Christie's.
6. **Une lecture fausse publiée se corrige visiblement** : laisser la mention « correction » dans le fichier de résultats avec la date, ne pas effacer.
7. **Prévoir la relance avant de fermer** : une vente du soir à 18 h a ses prix Christie's en ligne vers 21 h, ses comptes rendus de presse vers 22 h et le lendemain matin ; Sotheby's Paris peut ne jamais publier lot par lot.
