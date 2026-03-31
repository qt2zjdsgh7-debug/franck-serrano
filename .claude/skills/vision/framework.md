# Framework Théorie des Jeux — Référence Complète

Ce document est la référence détaillée du framework utilisé par le skill `/vision`.

---

## Fondements conceptuels

### Qu'est-ce qu'un jeu ?

Un jeu au sens de la théorie des jeux est toute situation où :
1. **Au moins 2 joueurs** prennent des décisions
2. Les **gains de chacun dépendent des choix de tous**
3. Chaque joueur agit de manière **rationnelle** (maximise ses gains attendus)

### Types de jeux reconnus

| Type | Description | Exemple concret |
|------|-------------|-----------------|
| **Coopératif** | Joueurs peuvent former des coalitions contraignantes | Partenariat commercial |
| **Non coopératif** | Décisions indépendantes sans engagement contraignant | Concurrence sur un marché |
| **Somme nulle** | Le gain d'un joueur = la perte d'un autre | Négociation à valeur fixe |
| **Somme non nulle** | La valeur totale peut augmenter ou diminuer | Innovation collaborative |
| **Jeu séquentiel** | Les joueurs agissent à tour de rôle | Développement produit par itérations |
| **Jeu simultané** | Tous décident sans voir les choix des autres | Lancement simultané de produits |
| **Jeu répété** | Le même jeu se joue plusieurs fois | Relations long terme équipe/client |
| **Jeu à information incomplète** | Certains joueurs ignorent des paramètres | Recrutement, M&A |

---

## Les 7 Dimensions en détail

### Dimension 1 — JOUEURS (Players)

**Objectif** : Identifier et caractériser tous les acteurs qui ont une influence sur la situation.

**Grille d'analyse par joueur :**
- **Identité** : Qui est-il exactement ? (individu, équipe, organisation, système)
- **Objectif principal** : Que cherche-t-il à maximiser ?
- **Contraintes** : Qu'est-ce qui limite ses options ?
- **Ressources** : Qu'est-ce qui lui donne du pouvoir dans ce jeu ?
- **Rationalité** : Est-il pleinement rationnel, ou sujet à des biais ?
- **Horizon temporel** : Court terme ou long terme ?

**Erreurs fréquentes à éviter :**
- Oublier des joueurs passifs (régulateurs, opinion publique, futurs concurrents)
- Confondre un groupe hétérogène avec un seul joueur homogène
- Ignorer les joueurs internes (équipes, départements) dans une analyse organisationnelle

---

### Dimension 2 — STRATÉGIES (Strategy Space)

**Objectif** : Cartographier l'espace des actions possibles pour chaque joueur.

**Types de stratégies :**
- **Pure** : Un choix déterministe (toujours faire X)
- **Mixte** : Une distribution de probabilités sur les choix (faire X avec 70% de chance)
- **Dominante** : Meilleure indépendamment de ce que font les autres
- **Dominée** : Toujours pire qu'une autre stratégie — à éliminer

**Outil — Élimination itérative des stratégies dominées (EISD) :**
1. Identifier et éliminer les stratégies strictement dominées
2. Répéter jusqu'à ce que plus aucune ne soit dominée
3. Ce qui reste = l'espace de jeu rationnel

---

### Dimension 3 — GAINS (Payoff Matrix)

**Objectif** : Quantifier (ou ordonner qualitativement) les résultats pour chaque combinaison de stratégies.

**Structure d'une matrice de gains (2 joueurs, 2 stratégies) :**

```
                 Joueur B : Stratégie b1   Joueur B : Stratégie b2
Joueur A : a1      (gain_A, gain_B)           (gain_A, gain_B)
Joueur A : a2      (gain_A, gain_B)           (gain_A, gain_B)
```

**Dimensions des gains à évaluer :**
- Gains financiers directs
- Gains en position concurrentielle
- Gains en information ou apprentissage
- Coûts d'opportunité (ce à quoi on renonce)
- Effets de réseau et externalités

**Horizon temporel :**
- Gains immédiats (T+0 à T+3 mois)
- Gains à moyen terme (T+3 mois à T+1 an)
- Gains structurels (T+1 an et au-delà)

---

### Dimension 4 — ÉQUILIBRES (Equilibria)

**Équilibre de Nash :**
> Un profil de stratégies (s₁*, s₂*, ..., sₙ*) est un **équilibre de Nash** si aucun joueur ne peut améliorer son gain en déviant **unilatéralement**.

- Tout jeu fini a au moins un équilibre de Nash (en stratégies mixtes)
- Il peut y en avoir plusieurs → problème de coordination
- L'équilibre de Nash n'est pas nécessairement optimal collectivement

**Optimum de Pareto :**
> Un résultat est **Pareto-optimal** si on ne peut pas améliorer la situation d'un joueur sans détériorer celle d'un autre.

**Tension Nash vs Pareto — Le Dilemme du Prisonnier :**
```
               Coopérer    Dévier
Coopérer       (3, 3)      (0, 4)
Dévier         (4, 0)      (1, 1)  ← Équilibre de Nash (sous-optimal)
```
L'équilibre de Nash (Dévier, Dévier) → gains (1,1)
L'optimum de Pareto (Coopérer, Coopérer) → gains (3,3)

**Dans les jeux répétés :** La coopération peut émerger via des stratégies comme "Œil pour œil" (Tit-for-Tat) si l'horizon est suffisamment long.

---

### Dimension 5 — DOMINANCE & COALITIONS

**Stratégies dominantes :**
- **Strictement dominante** : Meilleure dans *tous* les scénarios
- **Faiblement dominante** : Meilleure ou égale dans tous les scénarios, meilleure dans au moins un

**Induction rétrograde (jeux séquentiels) :**
Analyser depuis la fin du jeu vers le début pour identifier les stratégies rationnelles à chaque nœud de décision.

**Théorie des coalitions :**
- **Valeur d'une coalition** v(S) : ce que le sous-groupe S peut obtenir en coopérant
- **Cœur du jeu** : ensemble des allocations stables (où aucune coalition ne préfère dévier)
- **Valeur de Shapley** : allocation équitable basée sur la contribution marginale de chaque joueur

**Questions clés :**
- Quelles coalitions créent de la valeur ?
- Lesquelles sont stables (le cœur est-il non vide) ?
- Y a-t-il un joueur pivot dont la présence est décisive ?

---

### Dimension 6 — INFORMATION & SIGNAUX

**Types d'information :**
- **Information complète** : tous connaissent les gains de tous
- **Information incomplète** : certains paramètres sont privés (types, coûts, intentions)
- **Information parfaite** : on voit toutes les actions passées (jeux séquentiels)
- **Information imparfaite** : certaines actions passées sont inobservables

**Asymétries d'information critiques :**

| Problème | Description | Mécanisme correcteur |
|----------|-------------|---------------------|
| **Sélection adverse** | Les "mauvais" types sont surreprésentés | Screening, certification |
| **Aléa moral** | Un agent prend des risques que supporte le principal | Incitations, monitoring |
| **Signalement** | Un type "fort" signale sa qualité | Signal coûteux (diplôme, garantie) |

**Cheap talk vs. signaux coûteux :**
- **Cheap talk** : déclarations sans coût → peu crédibles
- **Signal coûteux** : action dont le coût est supportable pour le "bon type" mais prohibitif pour le "mauvais type" → crédible

---

### Dimension 7 — MOUVEMENT STRATÉGIQUE

**Types de mouvements stratégiques :**

1. **Engagement** : rendre une stratégie irréversible pour la rendre crédible
   - Exemple : investissement public dans une technologie → signal d'intention forte

2. **Menace** : promettre une réponse punitive conditionnelle
   - Pour être crédible : le coût de la riposte doit être inférieur au gain de dissuasion

3. **Promesse** : s'engager à récompenser une action de l'autre
   - Même logique de crédibilité

4. **First-mover advantage** : agir en premier pour contraindre les choix des suivants

5. **Attente stratégique** : laisser l'autre se révéler avant d'agir

**Checklist du mouvement optimal :**
- [ ] Est-il crédible ? (l'autre a-t-il des raisons d'y croire ?)
- [ ] Est-il robuste ? (tient-il si les hypothèses changent légèrement ?)
- [ ] Anticipe-t-il les contre-mouvements ?
- [ ] Préserve-t-il les options futures ?
- [ ] Qui doit exécuter ce mouvement et avec quelles ressources ?

---

## Patterns récurrents

### Le Dilemme du Prisonnier
**Quand le reconnaître :** Deux parties auraient intérêt à coopérer mais la tentation de dévier est forte.
**Solution :** Jeu répété + mécanismes de réputation + contrats contraignants.

### Le Jeu de la Poule Mouillée (Chicken Game)
**Quand le reconnaître :** Deux parties foncent l'une vers l'autre, la première à dévier "perd la face" mais évite le crash.
**Solution :** Engagement crédible + signalement de détermination.

### Le Problème de Coordination
**Quand le reconnaître :** Plusieurs équilibres existent, les joueurs veulent converger mais ne savent pas lequel choisir.
**Solution :** Point focal (standard commun), communication, leader coordinateur.

### La Guerre d'Attrition
**Quand le reconnaître :** Deux joueurs attendent que l'autre abandonne, en supportant des coûts croissants.
**Solution :** Stratégie de sortie définie à l'avance, ou signal de capacité supérieure.

### Le Hold-Up
**Quand le reconnaître :** Un joueur fait un investissement spécifique qui le rend dépendant d'un autre.
**Solution :** Contrats ex-ante, intégration verticale, réputation.

---

## Checklist d'analyse complète

Avant de conclure une prise de vision, vérifier :

- [ ] Tous les joueurs pertinents sont identifiés, y compris les silencieux
- [ ] Les gains sont évalués du point de vue de chaque joueur (pas seulement le nôtre)
- [ ] L'équilibre de Nash est identifié
- [ ] La distance entre équilibre Nash et optimum Pareto est mesurée
- [ ] Les asymétries d'information critiques sont listées
- [ ] Le mouvement recommandé est crédible et robuste
- [ ] Les signaux d'alerte qui invalideraient l'analyse sont précisés
