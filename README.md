# Automatisation Claude Code

Configuration d'automatisation avec Claude Code basée sur le tutoriel de Aurelien Fagioli.

## Fonctionnalités configurées

### 1. Tâches planifiées (Scheduled Tasks)

Configurées dans `.claude/settings.json` :

| Tâche | Fréquence | Description |
|-------|-----------|-------------|
| `daily-summary` | Chaque jour à 8h | Résumé emails + calendrier |
| `weekly-report` | Chaque lundi à 9h | Rapport hebdomadaire d'activité |
| `email-followup` | Chaque jour à 10h | Emails sans réponse depuis +3 jours |

### 2. Connecteurs natifs (MCP)

- **Gmail** : Lecture/analyse des emails
- **Google Calendar** : Consultation des événements

### 3. Commande /loop

Utiliser `/loop` pour exécuter des tâches en boucle :
```
/loop 30m Vérifie les nouveaux emails importants et résume-les
```

## Installation

### Prérequis
- Claude Code installé
- Node.js 18+

### Configurer Gmail et Calendar
```bash
chmod +x scripts/setup-gmail.sh scripts/setup-calendar.sh
./scripts/setup-gmail.sh
./scripts/setup-calendar.sh
```

### Activer les tâches planifiées
Les tâches sont déjà configurées dans `.claude/settings.json`.
Elles s'activeront automatiquement au prochain démarrage de Claude Code.

## Structure du projet

```
.
├── .claude/
│   └── settings.json          # Config Claude Code (tâches planifiées, MCP, permissions)
├── automations/
│   ├── daily-summary.md       # Résumé quotidien (généré automatiquement)
│   ├── weekly-report.md       # Rapport hebdomadaire (généré automatiquement)
│   └── followup-needed.md     # Suivi emails (généré automatiquement)
├── scripts/
│   ├── setup-gmail.sh         # Script installation Gmail MCP
│   └── setup-calendar.sh      # Script installation Calendar MCP
└── README.md
```

## Utilisation du /loop

La commande `/loop` permet de faire tourner Claude en continu :

```bash
# Surveillance emails toutes les 30 minutes
/loop 30m Vérifie mes nouveaux emails et répond aux urgences

# Monitoring toutes les heures
/loop 1h Analyse les nouvelles opportunités dans mes emails et résume-les
```

> **Note** : Le /loop a une limite de 3 jours en continu.

## Hébergement sur VPS (Agent 24/7)

Pour faire tourner l'agent en permanence :

```bash
# Sur votre VPS, installer Claude Code
npm install -g @anthropic-ai/claude-code

# Lancer en arrière-plan avec screen
screen -S claude-agent
claude --dangerously-skip-permissions

# Détacher : Ctrl+A puis D
# Réattacher : screen -r claude-agent
```

## Références

- Tutoriel vidéo : https://www.youtube.com/watch?v=kYTgB1uNn5E
- Contact : automatisation@aurelienfagioli.fr
