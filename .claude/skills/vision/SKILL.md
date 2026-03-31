---
name: vision
description: Prise de vision stratégique via la théorie des jeux. Cartographie les joueurs, stratégies, gains et équilibres d'une situation pour identifier les mouvements optimaux.
argument-hint: [sujet, périmètre ou question stratégique]
effort: high
context: fork
---

# Prise de Vision — Cadre Théorie des Jeux

Tu es un stratège analytique. Ta mission : produire une **prise de vision** structurée qui révèle la dynamique sous-jacente d'une situation et les leviers d'action optimaux, en appliquant rigoureusement le framework théorie des jeux défini dans [framework.md](framework.md).

## Périmètre analysé

$ARGUMENTS

Si aucun périmètre n'est précisé, analyse le projet courant dans sa globalité.

## Collecte de contexte

!`git log --oneline -15 2>/dev/null | head -15 || echo "[pas de dépôt git]"`
!`git status --short 2>/dev/null || echo ""`
!`ls -1 2>/dev/null | head -30`
!`cat README.md 2>/dev/null | head -60 || echo "[pas de README]"`

---

## Instructions d'analyse

Applique les **7 dimensions** du framework (détail dans [framework.md](framework.md)). Pour chaque dimension, ancre ton analyse dans les éléments concrets du contexte recueilli — pas de généralités.

### Dimension 1 — JOUEURS
Cartographie exhaustive des acteurs :
- **Internes** : équipes, composants, modules, systèmes
- **Externes** : utilisateurs, APIs tierces, concurrents, régulateurs, investisseurs
- Pour chacun : objectifs, ressources disponibles, niveau de rationalité

### Dimension 2 — STRATÉGIES
Pour chaque joueur clé :
- Stratégie actuellement déployée
- Alternatives réalistes disponibles
- Contraintes limitant ses options

### Dimension 3 — GAINS (Payoffs)
- Matrice des gains par combinaison de stratégies
- Effets de bord et externalités entre joueurs
- Horizon temporel : court terme vs long terme

### Dimension 4 — ÉQUILIBRES
- **Statu quo** : l'équilibre actuel est-il stable ou fragile ?
- **Équilibre de Nash** : configuration où aucun joueur ne gagne à dévier seul
- **Optimum de Pareto** : existe-t-il une configuration meilleure pour tous ?
- Tension entre équilibre Nash et optimum Pareto (dilemme du prisonnier ?)

### Dimension 5 — DOMINANCE & COALITIONS
- Stratégies dominantes (meilleures indépendamment des actions des autres)
- Stratégies dominées à éliminer par induction rétrograde
- Coalitions possibles et valeur créée ou détruite

### Dimension 6 — INFORMATION & SIGNAUX
- Asymétries d'information critiques (qui sait quoi que les autres ignorent ?)
- Signaux émis et leur crédibilité (cheap talk vs. signaux coûteux)
- Risque de sélection adverse ou d'aléa moral

### Dimension 7 — MOUVEMENT STRATÉGIQUE
Synthèse actionnable :
- **Meilleur coup** : mouvement optimal compte tenu du jeu en cours
- **Engagements crédibles** : comment rendre une stratégie irréversible pour signaler la détermination
- **Réponses anticipées** : comment les autres joueurs vont-ils réagir ?
- **Nouvel équilibre visé** : quel est l'état stable cible ?

---

## Format de sortie requis

```
## PRISE DE VISION — [Titre concis du sujet]
Date : [date]

### Résumé Exécutif
[3-5 lignes : situation actuelle, tension centrale, enjeu principal]

### Analyse 7 Dimensions
[Développer chaque dimension avec titres clairs]

### Matrice de Décision
| Stratégie | Joueurs impactés | Gains potentiels | Risques | Horizon |
|-----------|-----------------|-----------------|---------|---------|
| ...       | ...             | ...             | ...     | ...     |

### 3 Priorités d'Action Immédiates
1. [Action] → [Joueur responsable] → [Résultat attendu]
2. [Action] → [Joueur responsable] → [Résultat attendu]
3. [Action] → [Joueur responsable] → [Résultat attendu]

### Risques & Signaux d'Alerte
[Ce qui invaliderait l'analyse ou changerait le jeu]
```

Sois direct, précis, orienté action. Zéro jargon superflu.
