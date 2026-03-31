"""Dashboard terminal Rich pour visualiser et gérer les messages WeChat analysés."""

from __future__ import annotations

import threading
from typing import List, Optional

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from .models import (
    URGENCY_COLORS,
    URGENCY_ICONS,
    URGENCY_LABELS,
    URGENCY_ORDER,
    MessageAnalysis,
    UrgencyLevel,
)

console = Console()


class Dashboard:
    """Affiche, trie et permet de répondre aux messages analysés."""

    def __init__(self) -> None:
        self._analyses: List[MessageAnalysis] = []
        self._lock = threading.Lock()

    # ──────────────────────────────────────────────────────────
    # Ajout d'une analyse (thread-safe, depuis le worker)
    # ──────────────────────────────────────────────────────────

    def add(self, analysis: MessageAnalysis) -> None:
        with self._lock:
            self._analyses.append(analysis)
            self._analyses.sort(
                key=lambda a: URGENCY_ORDER.index(a.urgency)
            )

        # Notification immédiate pour les messages critiques / urgents
        if analysis.urgency in (UrgencyLevel.CRITICAL, UrgencyLevel.HIGH):
            self._alert(analysis)

    def _alert(self, analysis: MessageAnalysis) -> None:
        icon = URGENCY_ICONS[analysis.urgency]
        color = URGENCY_COLORS[analysis.urgency]
        console.print(
            f"\n{icon} [{color}]Nouveau message {URGENCY_LABELS[analysis.urgency]}[/{color}] "
            f"— [bold]{analysis.message.sender_name}[/bold] : {analysis.summary}"
        )

    # ──────────────────────────────────────────────────────────
    # Affichage de la liste
    # ──────────────────────────────────────────────────────────

    def show_list(self, show_all: bool = False) -> None:
        with self._lock:
            items = list(self._analyses)

        pending = [a for a in items if not a.responded]
        done = [a for a in items if a.responded]

        if not pending:
            if done:
                console.print("[dim]Tous les messages ont été traités. ✓[/dim]")
            else:
                console.print("[dim]Aucun message pour l'instant.[/dim]")
            return

        table = Table(
            title=f"📱  Messages WeChat en attente ({len(pending)})",
            box=box.ROUNDED,
            header_style="bold cyan",
            show_lines=True,
            expand=False,
        )
        table.add_column("#", style="dim", width=3, justify="right")
        table.add_column("Urgence", width=18)
        table.add_column("De", style="bold", min_width=12, max_width=20)
        table.add_column("Résumé", min_width=35, max_width=55)
        table.add_column("Heure", style="dim", width=6, justify="right")

        for i, analysis in enumerate(pending, start=1):
            color = URGENCY_COLORS[analysis.urgency]
            icon = URGENCY_ICONS[analysis.urgency]
            label = URGENCY_LABELS[analysis.urgency]

            sender = analysis.message.sender_name
            if analysis.message.is_group:
                sender += f"\n[dim]({analysis.message.group_name})[/dim]"

            table.add_row(
                str(i),
                Text(f"{icon}  {label}", style=color),
                sender,
                analysis.summary,
                analysis.message.timestamp.strftime("%H:%M"),
            )

        console.print(table)

        if show_all and done:
            console.print(f"[dim]{len(done)} message(s) déjà traité(s).[/dim]")

    # ──────────────────────────────────────────────────────────
    # Détail + choix de réponse
    # ──────────────────────────────────────────────────────────

    def review(self, index: int) -> Optional[tuple[MessageAnalysis, str]]:
        """Affiche le détail du message N et propose une réponse.

        Retourne (analysis, texte_de_réponse) ou None si ignoré.
        """
        with self._lock:
            pending = [a for a in self._analyses if not a.responded]

        if not 1 <= index <= len(pending):
            console.print(f"[red]Numéro invalide. Entrez entre 1 et {len(pending)}.[/red]")
            return None

        analysis = pending[index - 1]
        msg = analysis.message

        console.print()
        console.print(Rule(f"Message #{index} — {msg.sender_name}", style="cyan"))

        # En-tête info
        meta_parts = [
            f"[bold]Expéditeur :[/bold] {msg.sender_name}",
            f"[bold]Heure :[/bold] {msg.timestamp.strftime('%d/%m/%Y %H:%M')}",
        ]
        if msg.is_group:
            meta_parts.append(f"[bold]Groupe :[/bold] {msg.group_name}")
        console.print("  " + "   |   ".join(meta_parts))
        console.print()

        # Contenu du message
        console.print(
            Panel(
                msg.content,
                title="💬 Message reçu",
                border_style="white",
                padding=(1, 2),
            )
        )

        # Analyse Claude
        color = URGENCY_COLORS[analysis.urgency]
        icon = URGENCY_ICONS[analysis.urgency]
        label = URGENCY_LABELS[analysis.urgency]
        console.print(
            f"\n  {icon} [{color}]{label}[/{color}]  —  [italic]{analysis.urgency_reason}[/italic]"
        )
        console.print()

        # Suggestions de réponse
        console.print("[bold cyan]Réponses suggérées :[/bold cyan]")
        for i, suggestion in enumerate(analysis.suggested_responses, start=1):
            console.print(f"  [bold]{i}.[/bold]  {suggestion}")

        console.print(
            f"\n  [bold]{len(analysis.suggested_responses) + 1}.[/bold]  "
            "Écrire une réponse personnalisée"
        )
        console.print("  [bold]0.[/bold]  Ignorer / marquer comme lu\n")

        nb_choices = len(analysis.suggested_responses) + 1
        choice = IntPrompt.ask("Votre choix", default=0)

        if choice == 0:
            with self._lock:
                analysis.responded = True
            console.print("[dim]Message ignoré.[/dim]")
            return None

        if 1 <= choice <= len(analysis.suggested_responses):
            selected = analysis.suggested_responses[choice - 1]
        elif choice == nb_choices:
            selected = Prompt.ask("[cyan]Votre réponse[/cyan]")
        else:
            console.print("[red]Choix invalide.[/red]")
            return None

        with self._lock:
            analysis.responded = True
            analysis.selected_response = selected

        console.print(
            Panel(
                f"[green]{selected}[/green]",
                title="✅ Réponse sélectionnée",
                border_style="green",
            )
        )
        return analysis, selected

    # ──────────────────────────────────────────────────────────
    # Statistiques rapides
    # ──────────────────────────────────────────────────────────

    def show_stats(self) -> None:
        with self._lock:
            items = list(self._analyses)

        if not items:
            console.print("[dim]Aucune statistique disponible.[/dim]")
            return

        total = len(items)
        pending = sum(1 for a in items if not a.responded)
        by_urgency = {lvl: 0 for lvl in UrgencyLevel}
        for a in items:
            by_urgency[a.urgency] += 1

        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Clé", style="dim")
        table.add_column("Valeur", style="bold")

        table.add_row("Total reçus", str(total))
        table.add_row("En attente", str(pending))
        table.add_row("Traités", str(total - pending))
        table.add_row("", "")
        for lvl in URGENCY_ORDER:
            icon = URGENCY_ICONS[lvl]
            label = URGENCY_LABELS[lvl]
            color = URGENCY_COLORS[lvl]
            table.add_row(
                f"{icon} {label}",
                Text(str(by_urgency[lvl]), style=color),
            )

        console.print(Panel(table, title="📊 Statistiques", border_style="cyan"))
