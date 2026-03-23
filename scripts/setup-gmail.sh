#!/bin/bash
# Script de configuration Gmail MCP pour Claude Code
# Basé sur le tutoriel : https://www.youtube.com/watch?v=kYTgB1uNn5E

set -e

echo "=== Configuration Gmail MCP pour Claude Code ==="
echo ""

# Vérifier les prérequis
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé. Installez-le depuis https://nodejs.org"
    exit 1
fi

if ! command -v npx &> /dev/null; then
    echo "❌ npx n'est pas disponible. Installez Node.js avec npm."
    exit 1
fi

echo "✅ Node.js détecté : $(node --version)"
echo ""

# Instructions pour obtenir les credentials Google
echo "📋 Étapes pour configurer Gmail :"
echo ""
echo "1. Allez sur https://console.cloud.google.com"
echo "2. Créez un nouveau projet ou sélectionnez un existant"
echo "3. Activez l'API Gmail : APIs & Services > Enable APIs > Gmail API"
echo "4. Créez des identifiants OAuth 2.0 : APIs & Services > Credentials"
echo "5. Téléchargez le fichier credentials.json"
echo "6. Placez-le dans : ~/.gmail-credentials.json"
echo ""

# Tester l'installation du serveur MCP Gmail
echo "🔧 Installation du serveur MCP Gmail..."
npx -y @modelcontextprotocol/server-gmail --version 2>/dev/null || echo "Note: Le serveur sera installé à la première utilisation"

echo ""
echo "✅ Configuration terminée !"
echo ""
echo "Ajoutez dans votre .claude/settings.json :"
echo '{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gmail"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "~/.gmail-credentials.json"
      }
    }
  }
}'
