#!/usr/bin/env python3
"""
Automated Daily Hackathon Scheduler
Runs continuously in the background and fetches latest hackathons at your specified time every day.
"""
import argparse
import datetime
import os
import sys
import time
from hackathons.aggregator import HackathonAggregator
from hackathons.notifiers import send_telegram_alert, send_discord_webhook

def run_sync():
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now_str}] 🚀 Running automated hackathon sync...")
    
    aggregator = HackathonAggregator()
    hackathons = aggregator.fetch_all(force_refresh=True)
    print(f"[{now_str}] ✓ Fetched {len(hackathons)} active hackathons across all platforms.")

    # Export markdown and json
    with open("HACKATHONS.md", "w", encoding="utf-8") as f:
        f.write(aggregator.export_markdown(hackathons))
    with open("hackathons.json", "w", encoding="utf-8") as f:
        f.write(aggregator.export_json(hackathons))
    print(f"[{now_str}] ✓ Saved to HACKATHONS.md and hackathons.json.")

    # Send alerts if configured
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        ok = send_telegram_alert(hackathons)
        print(f"[{now_str}] {'✓ Telegram alert delivered!' if ok else '✗ Telegram alert failed.'}")

    if os.getenv("DISCORD_WEBHOOK_URL"):
        ok = send_discord_webhook(hackathons)
        print(f"[{now_str}] {'✓ Discord webhook delivered!' if ok else '✗ Discord webhook failed.'}")

def main():
    parser = argparse.ArgumentParser(description="Automated Daily Hackathon Scheduler")
    parser.add_argument("--time", type=str, default="09:00", help="Daily execution time in 24h format HH:MM (e.g. 09:00, 18:30)")
    parser.add_argument("--now", action="store_true", help="Run immediately once then wait for next scheduled time")
    args = parser.parse_args()

    print("=" * 65)
    print("🤖 AUTOMATED HACKATHON SCHEDULER")
    print(f"⏰ Scheduled to run daily at: {args.time}")
    print("=" * 65)

    if args.now:
        run_sync()

    target_hour, target_minute = map(int, args.time.split(":"))

    while True:
        now = datetime.datetime.now()
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        if now >= target:
            target += datetime.timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        hours = int(wait_seconds // 3600)
        minutes = int((wait_seconds % 3600) // 60)
        print(f"⏳ Next sync scheduled at {target.strftime('%Y-%m-%d %H:%M:%S')} (in {hours}h {minutes}m). Waiting...")

        # Sleep until target time
        time.sleep(wait_seconds + 1)
        run_sync()

if __name__ == "__main__":
    main()
