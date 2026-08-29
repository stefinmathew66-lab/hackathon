#!/usr/bin/env python3
"""
Automated Daily Hackathon Scheduler
Runs continuously in the background and fetches latest hackathons at 8:00 AM every day.
Sends personal alerts to WhatsApp (CallMeBot) and broadcasts to Telegram Channel.
"""
import argparse
import datetime
import os
import sys
import time
from dotenv import load_dotenv
from hackathons.aggregator import HackathonAggregator
from hackathons.notifiers import send_telegram_alert, send_whatsapp_alert, send_discord_webhook

load_dotenv()

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

    # 1. Personal WhatsApp Alert (CallMeBot)
    if os.getenv("WHATSAPP_PHONE") and os.getenv("WHATSAPP_APIKEY"):
        ok_wa = send_whatsapp_alert(hackathons)
        print(f"[{now_str}] {'✓ Personal WhatsApp digest delivered!' if ok_wa else '✗ WhatsApp delivery failed.'}")

    # 2. Telegram Community Broadcast
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        ok_tg = send_telegram_alert(hackathons)
        print(f"[{now_str}] {'✓ Telegram channel broadcast delivered!' if ok_tg else '✗ Telegram broadcast failed.'}")

    # 3. Discord Webhook
    if os.getenv("DISCORD_WEBHOOK_URL"):
        ok_dc = send_discord_webhook(hackathons)
        print(f"[{now_str}] {'✓ Discord webhook delivered!' if ok_dc else '✗ Discord webhook failed.'}")

def main():
    parser = argparse.ArgumentParser(description="Automated Daily Hackathon Scheduler")
    parser.add_argument("--time", type=str, default="08:00", help="Daily execution time in 24h format HH:MM (default: 08:00)")
    parser.add_argument("--now", action="store_true", help="Run immediately once then wait for next scheduled time")
    args = parser.parse_args()

    print("=" * 65)
    print("🤖 AUTOMATED HACKATHON SCHEDULER")
    print(f"⏰ Scheduled to run daily at: {args.time} IST")
    print("📱 Personal Alerts: WhatsApp (CallMeBot)")
    print("📢 Broadcasts: Telegram Channel")
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
