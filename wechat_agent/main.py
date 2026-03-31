"""Orchestrateur principal de l'agent WeChat."""

from __future__ import annotations

import logging
import queue
import threading
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich import box

from .analyzer import MessageAnalyzer
from .dashboard import Dashboard
from .models import WeChatMessage

console = Console()
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Messages de démo multilingues
# ──────────────────────────────────────────────────────────────────────────────

_DEMO_MESSAGES = [
    {
        "sender": "Marie Dupont",
        "content": (
            "Salut ! Le client vient de m'appeler, il est furieux — le rapport "
            "devait être envoyé à 10h et il est toujours pas parti. "
            "Il menace d'annuler le contrat. URGENT !!!"
        ),
        "group": None,
    },
    {
        "sender": "Papa",
        "content": "Bonjour fils. Tu viens dimanche pour le repas de famille ? Maman prépare le couscous 😊",
        "group": None,
    },
    {
        "sender": "Zhang Wei",
        "content": "你好！明天下午3点的会议，你准备好演示文稿了吗？客户很重要。",
        "group": None,
    },
    {
        "sender": "Sophie Admin",
        "content": "Réunion budgétaire reportée à jeudi 14h. Merci de confirmer ta présence.",
        "group": "Équipe Direction",
    },
    {
        "sender": "DevOps Bot",
        "content": (
            "🚨 ALERTE : Le serveur de production api.prod-01 ne répond plus. "
            "CPU à 100 % depuis 5 min. Intervention requise maintenant."
        ),
        "group": "Équipe Tech",
    },
    {
        "sender": "Lucas",
        "content": "T'as vu le match hier ? Incroyable ce but en fin de match 🔥",
        "group": None,
    },
]


class WeChatAgent:
    """Agent principal : réception, analyse et interface utilisateur."""

    def __init__(self, api_key: str, model: str = "claude-opus-4-6") -> None:
        self.analyzer = MessageAnalyzer(api_key=api_key, model=model)
        self.dashboard = Dashboard()
        self._queue: queue.Queue[WeChatMessage] = queue.Queue()
        self._running = False
        self._wechat: Optional[object] = None

    # ──────────────────────────────────────────────────────────
    # Points d'entrée publics
    # ──────────────────────────────────────────────────────────

    def run_with_wechat(self) -> None:
        """Mode itchat : connexion WeChat via QR code."""
        from .wechat_client import WeChatClient

        console.print("[bold green]Connexion à WeChat (itchat)…[/bold green]")
        wechat = WeChatClient(on_message=self._enqueue)
        wechat.login()
        wechat.run_async()
        console.print("[bold green]✓ Connecté à WeChat[/bold green]")
        self._wechat = wechat
        self._interactive_loop()
        wechat.logout()

    def run_manual(self) -> None:
        """Mode manuel : messages collés dans le terminal."""
        from .wechat_client import ManualInputClient

        client = ManualInputClient(on_message=self._enqueue)
        # Le worker d'analyse tourne en arrière-plan
        self._start_worker()
        # La lecture bloquante dans le thread principal
        try:
            client.read_loop()
        finally:
            self._running = False
            console.print("\n[dim]Mode manuel terminé.[/dim]")
            self.dashboard.show_stats()

    def run_demo(self) -> None:
        """Mode démo : injection de messages fictifs pour tester."""
        self._interactive_loop(inject_demo=True)

    # ──────────────────────────────────────────────────────────
    # Boucle interactive
    # ──────────────────────────────────────────────────────────

    def _interactive_loop(self, inject_demo: bool = False) -> None:
        self._start_worker()

        if inject_demo:
            self._inject_demo_messages()

        self._print_help()

        while self._running:
            try:
                cmd = Prompt.ask("\n[bold cyan]>[/bold cyan]", default="l").strip().lower()
            except (KeyboardInterrupt, EOFError):
                break

            if cmd in ("q", "quit", "exit"):
                break
            elif cmd in ("l", "ls", "liste", "list"):
                self.dashboard.show_list()
            elif cmd in ("s", "stats"):
                self.dashboard.show_stats()
            elif cmd in ("d", "demo"):
                self._inject_demo_messages()
                console.print(f"[green]{len(_DEMO_MESSAGES)} messages de démo injectés.[/green]")
            elif cmd in ("h", "help", "aide"):
                self._print_help()
            elif cmd.startswith("r"):
                # Accepte "r", "r3", "r 3", "review 3"
                parts = cmd.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    idx = int(parts[-1])
                elif len(parts) == 1 and len(parts[0]) > 1 and parts[0][1:].isdigit():
                    idx = int(parts[0][1:])
                else:
                    idx = IntPrompt.ask("Numéro du message")
                result = self.dashboard.review(idx)
                if result and self._wechat is not None:
                    analysis, text = result
                    self._send_response(analysis.message.sender_id, text)
            else:
                console.print("[dim]Commande inconnue. Tapez [bold]h[/bold] pour l'aide.[/dim]")

        self._running = False
        console.print("\n[dim]Agent arrêté.[/dim]")

    # ──────────────────────────────────────────────────────────
    # Worker d'analyse (thread séparé)
    # ──────────────────────────────────────────────────────────

    def _start_worker(self) -> None:
        self._running = True
        t = threading.Thread(target=self._analysis_worker, daemon=True)
        t.start()

    def _analysis_worker(self) -> None:
        while self._running:
            try:
                msg = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue
            try:
                console.print(
                    f"[dim]  ⏳ Analyse en cours : {msg.sender_name}…[/dim]"
                )
                analysis = self.analyzer.analyze(msg)
                self.dashboard.add(analysis)
            except Exception as exc:
                logger.error("Erreur analyse message : %s", exc)
                console.print(f"[red]Erreur analyse : {exc}[/red]")
            finally:
                self._queue.task_done()

    def _enqueue(self, msg: WeChatMessage) -> None:
        self._queue.put(msg)

    # ──────────────────────────────────────────────────────────
    # Envoi de réponse
    # ──────────────────────────────────────────────────────────

    def _send_response(self, user_id: str, text: str) -> None:
        try:
            self._wechat.send(user_id, text)  # type: ignore[union-attr]
            console.print("[green]✓ Message envoyé via WeChat.[/green]")
        except Exception as exc:
            console.print(
                f"[yellow]Réponse non envoyée (mode démo ou erreur réseau) : {exc}[/yellow]"
            )

    # ──────────────────────────────────────────────────────────
    # Démo
    # ──────────────────────────────────────────────────────────

    def _inject_demo_messages(self) -> None:
        for data in _DEMO_MESSAGES:
            msg = WeChatMessage(
                sender_name=data["sender"],
                sender_id=data["sender"].lower().replace(" ", "_"),
                content=data["content"],
                timestamp=datetime.now(),
                is_group=bool(data["group"]),
                group_name=data.get("group"),
            )
            self._enqueue(msg)

    # ──────────────────────────────────────────────────────────
    # Aide
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _print_help() -> None:
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 3))
        table.add_column("Commande", style="bold cyan", min_width=14)
        table.add_column("Description")
        table.add_row("l  (liste)", "Afficher les messages en attente")
        table.add_row("r N  (review)", "Lire le message N et choisir une réponse")
        table.add_row("s  (stats)", "Voir les statistiques")
        table.add_row("d  (demo)", "Injecter des messages de démo")
        table.add_row("h  (help)", "Afficher cette aide")
        table.add_row("q  (quit)", "Quitter l'agent")
        console.print(
            Panel(table, title="📖 Commandes disponibles", border_style="dim")
        )
