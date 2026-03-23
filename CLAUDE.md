# Instructions pour Claude Code

## Contexte du projet
Automatisation Claude Code avec Gmail et Google Calendar.
Basé sur le tutoriel de Aurelien Fagioli : https://www.youtube.com/watch?v=kYTgB1uNn5E

## Stack technique
- Claude Code CLI
- MCP : Gmail, Google Calendar
- Node.js 18+

## Structure
- `.claude/settings.json` — Configuration (MCP, tâches planifiées, permissions)
- `automations/` — Fichiers générés automatiquement par les tâches planifiées
- `scripts/` — Scripts d'installation des connecteurs MCP

## Conventions
- Les fichiers dans `automations/` sont générés automatiquement, ne pas modifier manuellement
- Les scripts dans `scripts/` doivent rester exécutables (`chmod +x`)
- Langue : français pour les messages et commentaires

## Avant de faire un commit
- Vérifier que les fichiers sensibles (clés API, credentials) ne sont pas inclus
- Utiliser un message de commit descriptif en français
