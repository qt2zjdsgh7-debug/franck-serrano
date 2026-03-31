"""Modèles de données pour l'agent WeChat."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid


class UrgencyLevel(Enum):
    """Niveau d'urgence d'un message."""
    CRITICAL = "critical"  # Réponse immédiate (crise, urgence)
    HIGH = "high"          # Répondre dans l'heure
    MEDIUM = "medium"      # Répondre dans la journée
    LOW = "low"            # Peut attendre


URGENCY_ORDER = [
    UrgencyLevel.CRITICAL,
    UrgencyLevel.HIGH,
    UrgencyLevel.MEDIUM,
    UrgencyLevel.LOW,
]

URGENCY_LABELS = {
    UrgencyLevel.CRITICAL: "CRITIQUE",
    UrgencyLevel.HIGH: "URGENT",
    UrgencyLevel.MEDIUM: "NORMAL",
    UrgencyLevel.LOW: "PEUT ATTENDRE",
}

URGENCY_COLORS = {
    UrgencyLevel.CRITICAL: "bold red",
    UrgencyLevel.HIGH: "bold yellow",
    UrgencyLevel.MEDIUM: "bold cyan",
    UrgencyLevel.LOW: "dim white",
}

URGENCY_ICONS = {
    UrgencyLevel.CRITICAL: "🔴",
    UrgencyLevel.HIGH: "🟡",
    UrgencyLevel.MEDIUM: "🔵",
    UrgencyLevel.LOW: "⚪",
}


@dataclass
class WeChatMessage:
    """Un message WeChat entrant."""
    sender_name: str
    sender_id: str
    content: str
    timestamp: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_group: bool = False
    group_name: Optional[str] = None
    message_type: str = "text"  # text, image, voice, file…


@dataclass
class MessageAnalysis:
    """Résultat de l'analyse Claude d'un message."""
    message: WeChatMessage
    urgency: UrgencyLevel
    urgency_reason: str
    summary: str
    suggested_responses: List[str]
    analyzed_at: datetime = field(default_factory=datetime.now)
    responded: bool = False
    selected_response: Optional[str] = None
