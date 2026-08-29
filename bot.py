#!/usr/bin/env python3
"""
Hackathon Link Fetcher & Bot CLI
Fetches latest hackathons across India & Global Online platforms for 100% free.
"""
import argparse
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from hackathons.aggregator import HackathonAggregator
from hackathons.notifiers import send_telegram_alert, send_discord_webhook

load_dotenv()
console = Console()

def display_banner():
    banner = """[bold cyan]
  _    _            _           _   _                  _    _             _   
 | |  | |          | |         | | | |                | |  | |           | |  
 | |__| | __ _  ___| | __ __ _ | |_| |__   ___  _ __  | |__| |_   _ _ __ | |_ 
 |  __  |/ _` |/ __| |/ // _` || __| '_ \ / _ \| '_ \ |  __  | | | | '_ \| __|
 | |  | | (_| | (__|   <| (_| || |_| | | | (_) | | | || |  | | |_| | | | | |_ 
 |_|  |_|\__,_|\___|_|\_\\__,_| \__|_| |_|\___/|_| |_||_|  |_|\__,_|_| |_|\__|
[/bold cyan]
[dim]⚡ 100% Free Multi-Source Hackathon Link Fetcher & Bot (India & Global Online)[/dim]
[dim]Platforms: Devfolio • Unstop • Devpost • HackerEarth • MLH[/dim]
"""
    console.print(banner)

def render_table(hackathons, limit=25):
    if not hackathons:
        console.print("[bold yellow]⚠️ No hackathons found matching criteria.[/bold yellow]")
        return

    table = Table(
        title=f"🚀 Latest Hackathons ({len(hackathons)} Opportunities Found)",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
        border_style="bright_blue"
    )

    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Platform", style="bold green", width=12)
    table.add_column("Title", style="bold white", width=34)
    table.add_column("Location / Mode", style="cyan", width=18)
    table.add_column("Prize Pool", style="gold1", width=18)
    table.add_column("Direct Link", style="bold underline blue")

    for idx, h in enumerate(hackathons[:limit], 1):
        mode = "🌐 Online" if h.is_online else (h.location or "In-Person")
        if h.is_india:
            mode += " [bold red](IN)[/bold red]"
        
        prize = h.prize_pool or "Swag & Prizes"
        table.add_row(
            str(idx),
            h.platform,
            h.title[:32] + ("..." if len(h.title) > 32 else ""),
            mode,
            prize[:16],
            f"[link={h.url}]{h.url}[/link]"
        )

    console.print(table)
    if len(hackathons) > limit:
        console.print(f"[dim]...showing {limit} of {len(hackathons)} items. Use --limit to view more.[/dim]\n")

def interactive_mode(aggregator: HackathonAggregator):
    while True:
        console.print("\n[bold cyan]Select an option:[/bold cyan]")
        console.print("1. 🇮🇳 View Latest Hackathons in India")
        console.print("2. 🌐 View Global Online Hackathons")
        console.print("3. 🔍 Search Hackathons by Keyword (AI, Web3, FinTech, etc.)")
        console.print("4. 🏢 Filter by Platform (Devfolio, Unstop, Devpost, HackerEarth, MLH)")
        console.print("5. 📊 Show Statistics & Platform Breakdown")
        console.print("6. 💾 Export Results to CSV / JSON / Markdown")
        console.print("7. 📢 Send Alert to Telegram / Discord")
        console.print("8. 🔄 Force Refresh Live Data")
        console.print("0. 🚪 Exit")

        choice = Prompt.ask("Enter choice", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"], default="1")

        if choice == "0":
            console.print("[green]Goodbye & happy hacking! 🚀[/green]")
            break
        elif choice == "1":
            with console.status("[bold green]Fetching India hackathons..."):
                results = aggregator.filter(india_only=True)
            render_table(results)
        elif choice == "2":
            with console.status("[bold green]Fetching Global Online hackathons..."):
                results = aggregator.filter(india_only=False, online_only=True)
            render_table(results)
        elif choice == "3":
            kw = Prompt.ask("Enter keyword to search")
            with console.status(f"[bold green]Searching for '{kw}'..."):
                results = aggregator.filter(query=kw)
            render_table(results)
        elif choice == "4":
            plat = Prompt.ask("Enter platform name (Devfolio, Unstop, Devpost, HackerEarth, MLH)")
            with console.status(f"[bold green]Filtering platform '{plat}'..."):
                results = aggregator.filter(platform=plat)
            render_table(results)
        elif choice == "5":
            stats = aggregator.get_stats()
            panel_content = (
                f"[bold green]Total Hackathons Found:[/bold green] {stats['total']}\n"
                f"[bold cyan]India Hackathons:[/bold cyan] {stats['india_total']}\n"
                f"[bold magenta]Global Online Hackathons:[/bold magenta] {stats['global_online_total']}\n"
                f"[bold yellow]Total Online / Virtual:[/bold yellow] {stats['online_total']}\n\n"
                f"[bold]Platform Breakdown:[/bold]\n"
                + "\n".join([f"  • {k}: [bold]{v}[/bold]" for k, v in stats['platforms'].items()])
                + f"\n\n[dim]Last Updated: {stats['last_updated']}[/dim]"
            )
            console.print(Panel(panel_content, title="📊 Aggregator Stats", border_style="green"))
        elif choice == "6":
            fmt = Prompt.ask("Choose format", choices=["markdown", "json", "csv"], default="markdown")
            filename = Prompt.ask("Enter filename to save", default=f"hackathons.{fmt if fmt != 'markdown' else 'md'}")
            data = aggregator.fetch_all()
            if fmt == "markdown":
                content = aggregator.export_markdown(data)
            elif fmt == "json":
                content = aggregator.export_json(data)
            else:
                content = aggregator.export_csv(data)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            console.print(f"[bold green]✓ Successfully exported {len(data)} hackathons to {filename}[/bold green]")
        elif choice == "7":
            target = Prompt.ask("Choose destination", choices=["telegram", "discord"], default="telegram")
            if target == "telegram":
                token = Prompt.ask("Telegram Bot Token (or press enter for env)", default=os.getenv("TELEGRAM_BOT_TOKEN", ""))
                chat_id = Prompt.ask("Telegram Chat ID (or press enter for env)", default=os.getenv("TELEGRAM_CHAT_ID", ""))
                success = send_telegram_alert(aggregator.fetch_all(), bot_token=token, chat_id=chat_id)
                console.print("[green]✓ Telegram message sent![/green]" if success else "[red]✗ Failed to send. Check bot token and chat ID.[/red]")
            else:
                webhook = Prompt.ask("Discord Webhook URL (or press enter for env)", default=os.getenv("DISCORD_WEBHOOK_URL", ""))
                success = send_discord_webhook(aggregator.fetch_all(), webhook_url=webhook)
                console.print("[green]✓ Discord webhook sent![/green]" if success else "[red]✗ Failed to send. Check webhook URL.[/red]")
        elif choice == "8":
            with console.status("[bold green]Refreshing live data from all platforms..."):
                results = aggregator.fetch_all(force_refresh=True)
            console.print(f"[bold green]✓ Refreshed! Total {len(results)} live hackathons loaded.[/bold green]")

def main():
    parser = argparse.ArgumentParser(description="Hackathon Link Fetcher & Bot CLI")
    parser.add_argument("--india", action="store_true", help="Filter hackathons in India")
    parser.add_argument("--online", action="store_true", help="Filter global online / virtual hackathons")
    parser.add_argument("--platform", type=str, help="Filter by platform (Devfolio, Unstop, Devpost, HackerEarth, MLH)")
    parser.add_argument("--search", type=str, help="Search keyword (AI, Web3, Student, etc.)")
    parser.add_argument("--limit", type=int, default=30, help="Number of results to display in table")
    parser.add_argument("--refresh", action="store_true", help="Force refresh data from sources")
    parser.add_argument("--export", type=str, help="Export results to file (.csv, .json, or .md)")
    parser.add_argument("--notify-telegram", action="store_true", help="Send alert to Telegram channel")
    parser.add_argument("--notify-discord", action="store_true", help="Send alert to Discord webhook")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive menu mode")

    args = parser.parse_args()
    display_banner()
    aggregator = HackathonAggregator()

    if args.interactive:
        interactive_mode(aggregator)
        return

    with console.status("[bold green]Fetching latest hackathons across all platforms..."):
        if args.india:
            results = aggregator.filter(india_only=True, query=args.search, platform=args.platform, force_refresh=args.refresh)
        elif args.online:
            results = aggregator.filter(online_only=True, india_only=False, query=args.search, platform=args.platform, force_refresh=args.refresh)
        else:
            results = aggregator.filter(query=args.search, platform=args.platform, force_refresh=args.refresh)

    render_table(results, limit=args.limit)

    if args.export:
        ext = args.export.split(".")[-1].lower()
        if ext == "json":
            content = aggregator.export_json(results)
        elif ext == "csv":
            content = aggregator.export_csv(results)
        else:
            content = aggregator.export_markdown(results)
        with open(args.export, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[bold green]✓ Exported {len(results)} hackathons to {args.export}[/bold green]")

    if args.notify_telegram:
        ok = send_telegram_alert(results)
        console.print("[green]✓ Sent to Telegram![/green]" if ok else "[yellow]⚠️ Telegram alert not sent. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env[/yellow]")

    if args.notify_discord:
        ok = send_discord_webhook(results)
        console.print("[green]✓ Sent to Discord![/green]" if ok else "[yellow]⚠️ Discord alert not sent. Set DISCORD_WEBHOOK_URL in .env[/yellow]")

if __name__ == "__main__":
    main()
