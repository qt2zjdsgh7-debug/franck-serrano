#!/usr/bin/env python3
"""
Agent WeChat — Point d'entrée principal.

Modes disponibles :
  --demo     Injecte des messages fictifs pour tester sans WeChat
  --manual   Collez vos messages manuellement dans le terminal
  (défaut)   Connexion WeChat via QR code (nécessite itchat)

Configuration :
  Définissez ANTHROPIC_API_KEY dans l'environnement ou dans un fichier .env
"""

import argparse
import os
import sys

from rich.console import Console
from rich.panel import Panel

console = Console()


def load_env() -> None:
    """Charge le fichier .env s'il existe."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv optionnel


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        console.print(
            "[red]❌ ANTHROPIC_API_KEY manquant.[/red]\n"
            "Ajoutez-le dans un fichier [bold].env[/bold] ou exportez-le :\n"
            "  [bold]export ANTHROPIC_API_KEY=sk-ant-...[/bold]"
        )
        sys.exit(1)
    return key


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent WeChat propulsé par Claude claude-opus-4-6",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--demo",
        action="store_true",
        help="Mode démo : injecte des messages fictifs pour tester",
    )
    group.add_argument(
        "--manual",
        action="store_true",
        help="Mode manuel : collez vos messages dans le terminal",
    )
    parser.add_argument(
        "--model",
        default="claude-opus-4-6",
        help="Modèle Claude à utiliser (défaut : claude-opus-4-6)",
    )
    args = parser.parse_args()

    load_env()
    api_key = get_api_key()

    console.print(
        Panel(
            "[bold cyan]🤖 Agent WeChat[/bold cyan]\n"
            "[dim]Propulsé par Claude claude-opus-4-6 · Adaptive Thinking activé[/dim]",
            border_style="cyan",
        )
    )

    from wechat_agent.main import WeChatAgent

    agent = WeChatAgent(api_key=api_key, model=args.model)

    if args.demo:
        console.print("[bold yellow]Mode démo[/bold yellow] — Aucune connexion WeChat requise.\n")
        agent.run_demo()
    elif args.manual:
        console.print("[bold yellow]Mode manuel[/bold yellow] — Collez vos messages ci-dessous.\n")
        agent.run_manual()
    else:
        try:
            agent.run_with_wechat()
        except ImportError as exc:
            console.print(f"[red]{exc}[/red]")
            console.print(
                "\n[yellow]Conseil :[/yellow] lancez en mode démo pour tester :\n"
                "  [bold]python run_agent.py --demo[/bold]"
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
