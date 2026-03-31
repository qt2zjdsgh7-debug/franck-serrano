"""Interface WeChat via la bibliothèque itchat.

itchat se connecte à WeChat Web par scan de QR code.
Note : WeChat a progressivement restreint la connexion web pour certains comptes.
Si la connexion échoue, utilisez le mode manuel (--manual) ou le mode démo (--demo).

Référence : https://itchat.readthedocs.io/
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable
import uuid

from .models import WeChatMessage

logger = logging.getLogger(__name__)

# Callback type : reçoit un WeChatMessage
MessageCallback = Callable[[WeChatMessage], None]


class WeChatClient:
    """Client WeChat utilisant itchat (scan QR code)."""

    def __init__(self, on_message: MessageCallback) -> None:
        self._on_message = on_message
        self._itchat = self._import_itchat()
        self._setup_handlers()

    # ──────────────────────────────────────────────────────────
    # Setup
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _import_itchat():
        """Importe itchat ou lève ImportError avec un message clair."""
        try:
            import itchat  # type: ignore
            return itchat
        except ImportError:
            raise ImportError(
                "itchat n'est pas installé. Lancez : pip install itchat\n"
                "Ou utilisez le mode manuel (--manual) / démo (--demo)."
            )

    def _setup_handlers(self) -> None:
        itchat = self._itchat

        @itchat.msg_register([itchat.content.TEXT])
        def _on_text(msg):  # type: ignore[return]
            self._handle(msg, is_group=False)

        @itchat.msg_register([itchat.content.TEXT], isGroupChat=True)
        def _on_group_text(msg):  # type: ignore[return]
            self._handle(msg, is_group=True)

    def _handle(self, raw_msg, is_group: bool) -> None:
        try:
            if is_group:
                wm = WeChatMessage(
                    sender_name=raw_msg.get("ActualNickName", "Inconnu"),
                    sender_id=raw_msg.get("ActualUserName", ""),
                    content=raw_msg.get("Text", ""),
                    timestamp=datetime.now(),
                    is_group=True,
                    group_name=raw_msg["User"].get("NickName", "Groupe"),
                )
            else:
                wm = WeChatMessage(
                    sender_name=raw_msg["User"].get("NickName", "Inconnu"),
                    sender_id=raw_msg["User"].get("UserName", ""),
                    content=raw_msg.get("Text", ""),
                    timestamp=datetime.now(),
                    is_group=False,
                )
            self._on_message(wm)
        except Exception as exc:  # pragma: no cover
            logger.error("Erreur traitement message WeChat : %s", exc)

    # ──────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────

    def login(self, hotReload: bool = True) -> None:
        """Lance la connexion WeChat (affiche un QR code dans le terminal)."""
        self._itchat.auto_login(hotReload=hotReload)

    def run_async(self) -> None:
        """Démarre la boucle de réception en arrière-plan (non-bloquant)."""
        self._itchat.run(blockThread=False)

    def send(self, to_user_id: str, text: str) -> None:
        """Envoie un message texte à un contact."""
        self._itchat.send(text, toUserName=to_user_id)

    def logout(self) -> None:
        """Déconnexion propre."""
        try:
            self._itchat.logout()
        except Exception:  # pragma: no cover
            pass


class ManualInputClient:
    """Mode manuel : l'utilisateur colle ses messages dans le terminal.

    Utile quand itchat n'est pas disponible ou que le compte WeChat
    ne supporte pas la connexion web.
    """

    def __init__(self, on_message: MessageCallback) -> None:
        self._on_message = on_message

    def read_loop(self) -> None:
        """Lit les messages collés dans stdin jusqu'à EOF (Ctrl+D)."""
        from rich.console import Console
        from rich.prompt import Prompt

        console = Console()
        console.print(
            "\n[bold cyan]Mode manuel[/bold cyan] — Collez vos messages WeChat ici.\n"
            "Format : [bold]NOM : message[/bold]  (ex: Alice : Rappelle-moi svp)\n"
            "Appuyez sur [bold]Entrée deux fois[/bold] pour soumettre, "
            "[bold]Ctrl+D[/bold] pour quitter.\n"
        )

        while True:
            try:
                lines: list[str] = []
                while True:
                    line = input()
                    if line == "" and lines:
                        break
                    lines.append(line)

                raw = "\n".join(lines).strip()
                if not raw:
                    continue

                # Essai de détecter "Nom : message"
                if ":" in raw:
                    sender, _, content = raw.partition(":")
                    sender = sender.strip()
                    content = content.strip()
                else:
                    sender = "Inconnu"
                    content = raw

                wm = WeChatMessage(
                    sender_name=sender,
                    sender_id=sender.lower().replace(" ", "_"),
                    content=content,
                    timestamp=datetime.now(),
                )
                self._on_message(wm)

            except EOFError:
                break
