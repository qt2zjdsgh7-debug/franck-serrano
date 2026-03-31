"""Analyseur de messages WeChat via Claude claude-opus-4-6.

Pour chaque message, Claude :
  1. Évalue l'urgence (critical / high / medium / low)
  2. Explique la raison
  3. Résume le message en une phrase
  4. Propose 3 formats de réponse adaptés
"""

import json
import re
import anthropic

from .models import WeChatMessage, MessageAnalysis, UrgencyLevel


# Prompt système – stable entre les appels → sera mis en cache automatiquement
_SYSTEM_PROMPT = """\
Tu es un assistant personnel expert en gestion des communications pour un utilisateur \
francophone qui reçoit des messages WeChat en français, en anglais et en chinois.

Ton rôle : analyser chaque message et retourner un objet JSON strict.

═══════════════════════════════════════
NIVEAUX D'URGENCE
═══════════════════════════════════════
• critical — Réponse immédiate requise.
  Ex : urgence médicale, crise professionnelle, deadline dépassée, appel à l'aide.

• high — Répondre dans l'heure.
  Ex : décision urgente, réunion imminente, validation bloquante, problème en prod.

• medium — Répondre dans la journée.
  Ex : coordination normale, question professionnelle, demande de rappel, invitation.

• low — Peut attendre ou ne pas répondre.
  Ex : salutation sans suite requise, partage de contenu, bavardage informel.

═══════════════════════════════════════
FORMAT DE RÉPONSE — JSON uniquement
═══════════════════════════════════════
{
  "urgency": "critical|high|medium|low",
  "urgency_reason": "Explication courte (1-2 phrases)",
  "summary": "Résumé du message en une phrase (langue de l'utilisateur : français)",
  "suggested_responses": [
    "Option courte et directe",
    "Option plus développée et formelle",
    "Option qui reporte / demande plus de temps"
  ]
}

Règles :
- Réponds UNIQUEMENT avec le JSON, sans balises markdown, sans commentaire.
- Les suggested_responses doivent être des messages prêts à être envoyés, \
adaptés au registre de la conversation (tutoiement/vouvoiement, formel/informel).
- Si le message est en chinois, les suggestions peuvent être en chinois ou en français \
selon le contexte.
"""


class MessageAnalyzer:
    """Analyse un message WeChat avec Claude claude-opus-4-6."""

    def __init__(self, api_key: str, model: str = "claude-opus-4-6") -> None:
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze(self, message: WeChatMessage) -> MessageAnalysis:
        """Appelle Claude pour classifier l'urgence et générer des suggestions."""
        user_content = self._build_context(message)

        # Streaming + adaptive thinking pour une évaluation nuancée.
        # get_final_message() récupère la réponse complète sans gérer les événements.
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            response = stream.get_final_message()

        data = self._parse_response(response)

        return MessageAnalysis(
            message=message,
            urgency=UrgencyLevel(data.get("urgency", "medium")),
            urgency_reason=data.get("urgency_reason", ""),
            summary=data.get("summary", message.content[:120]),
            suggested_responses=data.get("suggested_responses", []),
        )

    # ──────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _build_context(msg: WeChatMessage) -> str:
        lines = [f"Expéditeur : {msg.sender_name}"]
        if msg.is_group:
            lines.append(f"Groupe : {msg.group_name}")
        else:
            lines.append("Type : message direct (私信)")
        lines.append(f"Heure : {msg.timestamp.strftime('%H:%M le %d/%m/%Y')}")
        lines.append(f"Message : {msg.content}")
        return "\n".join(lines)

    @staticmethod
    def _parse_response(response) -> dict:
        """Extrait le JSON de la réponse Claude (ignore les blocs thinking)."""
        text = next(
            (block.text for block in response.content if block.type == "text"),
            "{}",
        )
        # Enlever d'éventuels blocs de code markdown
        text = re.sub(r"```(?:json)?\s*", "", text).strip()
        text = re.sub(r"```\s*$", "", text).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback : urgence moyenne, pas de suggestions
            return {
                "urgency": "medium",
                "urgency_reason": "Impossible de parser la réponse Claude.",
                "summary": text[:200],
                "suggested_responses": [],
            }
