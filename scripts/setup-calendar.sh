#!/bin/bash
# Script de configuration Google Calendar MCP pour Claude Code
# Basé sur le tutoriel : https://www.youtube.com/watch?v=kYTgB1uNn5E

set -e

echo "=== Configuration Google Calendar MCP pour Claude Code ==="
echo ""

# Vérifier les prérequis
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé. Installez-le depuis https://nodejs.org"
    exit 1
fi

echo "✅ Node.js détecté : $(node --version)"
echo ""

echo "📋 Étapes pour configurer Google Calendar :"
echo ""
echo "1. Allez sur https://console.cloud.google.com"
echo "2. Activez l'API Google Calendar : APIs & Services > Enable APIs"
echo "3. Réutilisez les credentials OAuth créés pour Gmail (ou créez-en de nouveaux)"
echo "4. Ajoutez le scope : https://www.googleapis.com/auth/calendar.readonly"
echo "5. Placez le fichier credentials dans : ~/.google-calendar-credentials.json"
echo ""

echo "✅ Configuration terminée !"
echo ""
echo "Ajoutez dans votre .claude/settings.json :"
echo '{
  "mcpServers": {
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-calendar"],
      "env": {
        "GOOGLE_CALENDAR_CREDENTIALS_PATH": "~/.google-calendar-credentials.json"
      }
    }
  }
}'
