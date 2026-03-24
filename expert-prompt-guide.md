# Guide Expert — Ingénierie de Prompts pour Claude

> Référence complète basée sur la documentation officielle Anthropic (2026) et les meilleures pratiques industrielles.
> Modèles couverts : Claude Opus 4.6 · Sonnet 4.6 · Haiku 4.5

---

## Table des matières

1. [Fondamentaux](#1-fondamentaux)
2. [Structure d'un prompt expert](#2-structure-dun-prompt-expert)
3. [Techniques essentielles](#3-techniques-essentielles)
4. [Contrôle du format de sortie](#4-contrôle-du-format-de-sortie)
5. [Raisonnement et Thinking](#5-raisonnement-et-thinking)
6. [Utilisation des outils](#6-utilisation-des-outils)
7. [Systèmes agentiques](#7-systèmes-agentiques)
8. [Techniques avancées](#8-techniques-avancées)
9. [Anti-patterns à éviter](#9-anti-patterns-à-éviter)
10. [Checklists et templates](#10-checklists-et-templates)

---

## 1. Fondamentaux

### Le principe du contrat

Claude interprète le system prompt comme un **contrat** : une description explicite et bornée de l'identité, des règles et du format attendu. Plus le contrat est précis, plus le comportement est prévisible.

> **Règle d'or :** Montre ton prompt à un collègue sans contexte. S'il est confus, Claude le sera aussi.

### Clarté avant longueur

Un prompt court et précis surpasse un prompt long et vague. Sois explicite sur :
- L'objectif final et les critères de succès
- Les contraintes (format, longueur, langue, ton)
- Ce que Claude doit faire — pas seulement ce qu'il ne doit pas faire

### Expliquer le pourquoi

Fournir le contexte derrière une règle permet à Claude de la généraliser intelligemment.

| Moins efficace | Plus efficace |
|---|---|
| `NEVER use ellipses` | `Never use ellipses — the text-to-speech engine can't pronounce them` |
| `Be concise` | `Limit your response to 3 sentences — it will appear in a mobile notification` |

---

## 2. Structure d'un prompt expert

### Ordre recommandé des éléments

```
1. Rôle / identité (une phrase)
2. Contexte général et motivation
3. Documents / données de référence  ← toujours avant la requête
4. Instructions détaillées et règles
5. Exemples (few-shot)
6. Format de sortie
7. Requête / input utilisateur       ← toujours en dernier
```

> **Important :** Pour les contextes longs (> 20 000 tokens), placer les documents *avant* la requête améliore les performances jusqu'à **+30 %**.

### Squelette de system prompt

```xml
You are [RÔLE EN UNE PHRASE].

<context>
[Contexte, motivation, audience cible]
</context>

<instructions>
1. [Règle 1]
2. [Règle 2]
3. [Règle 3]
</instructions>

<output_format>
[Description précise du format attendu]
</output_format>

<examples>
  <example>
    <input>[Exemple d'entrée]</input>
    <output>[Exemple de sortie idéale]</output>
  </example>
</examples>

If you are not certain about any fact, say so explicitly. Do not guess.
```

### Squelette de user prompt (template)

```xml
<input>
{{USER_INPUT}}
</input>

[Instruction principale]
```

---

## 3. Techniques essentielles

### 3.1 XML Tags — structure sémantique

Claude est **XML-natif** : les balises sont des conteneurs sémantiques, pas du formatage.

```xml
<instructions>Résume ce document en 3 points.</instructions>

<document>
{{DOCUMENT}}
</document>
```

Balises recommandées : `<instructions>`, `<context>`, `<input>`, `<output>`, `<examples>`, `<thinking>`, `<document>`, `<constraints>`, `<format>`.

### 3.2 Rôle ciblé

Une seule phrase suffit. Évite les personas trop élaborés.

```
You are a senior Python engineer specializing in performance optimization.
```

Au lieu d'un rôle rigide, décris la **perspective** souhaitée :
```
Analyze this architecture from a security-first perspective, prioritizing threat modeling over feature delivery.
```

### 3.3 Few-shot (3–5 exemples)

Les exemples sont plus fiables que les descriptions abstraites pour ancrer le format et le style.

```xml
<examples>
  <example>
    <input>Résume : "L'apprentissage automatique révolutionne..."</input>
    <output>L'IA transforme l'industrie en automatisant des tâches complexes.</output>
  </example>
  <example>
    <input>Résume : "La blockchain offre une transparence..."</input>
    <output>La blockchain garantit la traçabilité sans intermédiaire de confiance.</output>
  </example>
</examples>
```

**Règles :** pertinents (proches du cas réel), diversifiés (couvrent les cas limites), structurés (balises `<example>`).

### 3.4 Permission d'incertitude

Réduit drastiquement les hallucinations.

```
If you are not certain about any fact, explicitly state your uncertainty level
(high / medium / low confidence) rather than presenting assumptions as facts.
```

### 3.5 Critères de succès vérifiables

Claude doit pouvoir évaluer sa propre réponse.

```
A successful response:
- Is under 200 words
- Contains exactly 3 actionable recommendations
- Cites at least one specific metric
- Uses no jargon unfamiliar to a non-technical executive
```

---

## 4. Contrôle du format de sortie

### Dire quoi faire (pas quoi éviter)

| ❌ Moins efficace | ✅ Plus efficace |
|---|---|
| `Do not use markdown` | `Write in smoothly flowing prose paragraphs` |
| `Don't use bullet points` | `Present ideas as connected sentences within paragraphs` |
| `No long responses` | `Limit your response to 150 words` |

### Format JSON avec schéma

```
Return your analysis as valid JSON matching this schema exactly:
{
  "summary": string,         // 1-2 sentences
  "confidence": "high" | "medium" | "low",
  "recommendations": string[], // exactly 3 items
  "caveats": string | null
}
```

### Supprimer les préambules

```
Respond directly without preamble.
Do not start with phrases like "Here is...", "Based on...", "Certainly!".
```

### Prose sans markdown excessif

```xml
<avoid_excessive_markdown>
Write in clear, flowing prose using complete paragraphs. Reserve markdown only
for `inline code`, code blocks, and top-level headings (##). Do not use
**bold**, *italics*, or bullet lists unless the content is genuinely enumerable.
</avoid_excessive_markdown>
```

---

## 5. Raisonnement et Thinking

### Chain-of-Thought (CoT)

Pour les tâches complexes (analyse, code, math, décisions multi-critères) :

```
Before providing your answer, work through the problem step by step
in <thinking> tags. Show your reasoning, then give your final answer
outside the tags.
```

Dans les exemples few-shot, inclure le raisonnement dans `<thinking>` pour enseigner le pattern.

### Thinking adaptatif (Opus 4.6 / Sonnet 4.6)

```python
client.messages.create(
    model="claude-opus-4-6",
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},  # low | medium | high | max
    max_tokens=64000,
    messages=[...]
)
```

| Effort | Usage recommandé |
|---|---|
| `low` | Tâches simples, haute fréquence, latence sensible |
| `medium` | La plupart des cas (défaut conseillé) |
| `high` | Code complexe, analyse approfondie, agents |
| `max` | Opus 4.6 uniquement — problèmes très longs, recherche |

### Auto-vérification

```
Before finalizing your response, verify it against these criteria:
- [ ] Does it answer the exact question asked?
- [ ] Are all claims grounded in the provided context?
- [ ] Does it respect the required format?
```

### Activer le thinking étendu dans un skill

Inclure le mot `ultrathink` n'importe où dans le contenu du skill.

### Éviter la sur-réflexion

```
Choose an approach and commit to it. Avoid revisiting decisions unless
you encounter new information that directly contradicts your reasoning.
```

---

## 6. Utilisation des outils

### Framing impératif

```
# ❌
Can you suggest some changes to this function?

# ✅
Refactor this function to reduce its cyclomatic complexity.
```

### Appels parallèles

```xml
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between
them, make all independent calls in parallel. Never use placeholders or guess
missing parameters.
</use_parallel_tool_calls>
```

### Comportement proactif vs conservateur

**Proactif (implémente par défaut) :**
```xml
<default_to_action>
Implement changes rather than only suggesting them. If intent is unclear,
infer the most useful action and proceed, using tools to discover missing details.
</default_to_action>
```

**Conservateur (propose avant d'agir) :**
```xml
<do_not_act_before_instructions>
Do not modify files unless explicitly instructed. Default to research,
analysis, and recommendations. Only implement when the user explicitly requests it.
</do_not_act_before_instructions>
```

---

## 7. Systèmes agentiques

### Gestion du contexte long (multi-fenêtres)

```
Your context window will be automatically compacted as it approaches its limit.
Do not stop tasks early due to token budget concerns. As you approach the limit,
save your current progress and state to memory before the context refreshes.
Always be as persistent and autonomous as possible.
```

### Actions réversibles vs irréversibles

```
Consider the reversibility of each action before proceeding:
- Local, reversible actions (editing files, running tests): proceed freely
- Hard-to-reverse actions (git push --force, deleting files, external posts):
  ask for confirmation first
```

### Éviter la sur-ingénierie

```xml
<minimal_scope>
Only make changes directly requested or clearly necessary. Do not:
- Add features beyond what was asked
- Refactor surrounding code during a bug fix
- Add docstrings/comments to code you didn't change
- Create helpers for one-time operations
- Design for hypothetical future requirements
</minimal_scope>
```

### Suivi d'état structuré

```json
// tests.json — format structuré pour les états machine
{
  "tests": [
    {"id": 1, "name": "auth_flow", "status": "passing"},
    {"id": 2, "name": "user_api", "status": "failing"}
  ],
  "summary": {"total": 2, "passing": 1, "failing": 1}
}
```

```
// progress.txt — format libre pour les notes de progression
Session 3: Fixed auth token validation. Next: investigate user_api failure.
```

---

## 8. Techniques avancées

### Meta-prompting

Utiliser Claude pour améliorer ses propres prompts.

```
Here is a prompt draft I've written:
<draft_prompt>
{{PROMPT}}
</draft_prompt>

Analyze this prompt and:
1. Identify any ambiguities or missing constraints
2. Flag potential failure modes
3. Produce an improved version
```

### Prompt chaining

Décomposer une tâche complexe en appels API séquentiels.

```
Appel 1 → Génération du draft
Appel 2 → Révision critique contre critères
Appel 3 → Raffinement basé sur la critique
```

Utile quand la visibilité des étapes intermédiaires est requise.

### Confidence calibrée

```
For each factual claim, indicate your confidence:
- HIGH: well-established fact you are certain about
- MEDIUM: reasonable inference with some uncertainty
- LOW: speculation or extrapolation — flag clearly
```

### Simulation multi-perspectives

```
Analyze this decision from three perspectives:
1. A security engineer focused on attack surface
2. A product manager focused on user experience
3. A CTO focused on technical debt

Then synthesize a recommendation that balances all three views.
```

### RAG — structuration du contexte récupéré

```xml
<documents>
  <document index="1">
    <source>{{SOURCE_NAME}}</source>
    <document_content>{{RETRIEVED_CONTENT}}</document_content>
  </document>
</documents>

Find quotes from the documents that are directly relevant to the question,
place them in <quotes> tags, then answer based solely on those quotes.
```

### Constitutional prompting

Embarquer les règles éthiques et les limites dans le system prompt :

```
You are [ROLE].

<principles>
- Never fabricate citations, statistics, or quotes
- If a request conflicts with user safety, decline clearly and explain why
- Maintain user privacy: never store, repeat, or infer personal information
- When uncertain, say so rather than presenting assumptions as facts
</principles>
```

---

## 9. Anti-patterns à éviter

| Anti-pattern | Conséquence | Correction |
|---|---|---|
| Instructions vagues (`be helpful`) | Comportement imprévisible | Critères de succès précis |
| Tâches multiples dans un seul prompt | Attention fragmentée | Chainer les appels API |
| Instructions négatives seules (`don't use X`) | Moins fiable | Formuler positivement ce qu'il faut faire |
| Documents après la requête | -30 % de performance | Toujours documents → requête |
| Pas d'exemples pour les formats complexes | Format aléatoire | 3–5 exemples dans `<example>` |
| Pas de permission d'incertitude | Hallucinations confiantes | Ajouter la clause d'incertitude |
| Langage outil trop agressif (`MUST ALWAYS`) | Déclenchement excessif sur Opus 4.6 | `Use this tool when...` |
| Prompt édité directement en production | Régressions non détectées | Dev → staging → prod avec évals |
| Pas d'auto-vérification | Erreurs non détectées | Ajouter une étape de vérification finale |
| Rôle trop élaboré | Bruit, comportement instable | Une phrase de rôle, pas un roman |

---

## 10. Checklists et templates

### Checklist avant déploiement

```
AVANT D'ÉCRIRE
□ Les critères de succès sont définis et mesurables
□ Le modèle optimal est choisi (Haiku / Sonnet / Opus)
□ Le niveau d'effort est calibré (low / medium / high / max)

STRUCTURE DU PROMPT
□ Rôle défini en une phrase
□ XML tags utilisés pour séparer les sections
□ Documents placés avant la requête
□ 3–5 exemples few-shot si format critique
□ Critères de succès inclus
□ Format de sortie précisément décrit
□ Permission d'incertitude ajoutée
□ Auto-vérification finale demandée

AVANT PRODUCTION
□ Testé sur 5+ cas représentatifs (dont cas limites)
□ Cas d'hallucination potentiels identifiés et couverts
□ Version trackée (git / système de versioning)
□ Évaluation quantitative définie
```

### Template universel

```xml
<!-- SYSTEM PROMPT -->
You are [RÔLE EN UNE PHRASE].

<context>
[Contexte, audience, enjeux]
</context>

<instructions>
1. [Règle principale]
2. [Contraintes clés]
3. [Comportement face à l'incertitude]
</instructions>

<output_format>
[Format exact attendu : JSON / Markdown / prose / longueur / langue]
</output_format>

<examples>
  <example>
    <input>[Input type]</input>
    <output>[Output idéal]</output>
  </example>
</examples>

If you are not certain, say so explicitly. Do not guess.
Before finalizing, verify your response against the output format requirements.

<!-- USER PROMPT -->
<input>
{{USER_INPUT}}
</input>

[Instruction principale — toujours en dernier]
```

### Paramètres API recommandés par cas d'usage

| Cas d'usage | Modèle | Effort | Thinking |
|---|---|---|---|
| Classification, extraction simple | Haiku 4.5 | low | disabled |
| Rédaction, résumé, Q&A | Sonnet 4.6 | medium | disabled |
| Code, analyse technique | Sonnet 4.6 | medium | adaptive |
| Agent autonome multi-étapes | Opus 4.6 | high | adaptive |
| Recherche longue, migration complexe | Opus 4.6 | max | adaptive |

---

## Références

- [Anthropic — Prompting Best Practices (officiel)](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic — Prompt Engineering Overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [Anthropic — Interactive Tutorial (GitHub)](https://github.com/anthropics/prompt-eng-interactive-tutorial)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Prompting Guide — Techniques](https://www.promptingguide.ai/techniques)
- [Lakera — Ultimate Guide to Prompt Engineering 2026](https://www.lakera.ai/blog/prompt-engineering-guide)
