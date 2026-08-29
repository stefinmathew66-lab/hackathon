import logging
import os
from typing import List, Optional
import requests
from .models import Hackathon

logger = logging.getLogger(__name__)

def send_telegram_alert(
    hackathons: List[Hackathon],
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
    max_items: int = 8
) -> bool:
    """
    Sends latest hackathon links to a Telegram channel or chat for 100% free.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (or passed as arguments).
    """
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat:
        logger.warning("Telegram Bot Token or Chat ID not configured.")
        return False

    if not hackathons:
        return False

    message_lines = [
        "🔥 *LATEST HACKATHONS ALERT* 🔥\n",
        f"Found *{len(hackathons)}* opportunities matching your criteria:\n"
    ]

    for i, h in enumerate(hackathons[:max_items], 1):
        mode_icon = "🇮🇳" if h.is_india else "🌐"
        prize = h.prize_pool or "Swag & Prizes"
        title_safe = h.title.replace("*", "").replace("_", "").replace("[", "").replace("]", "")
        message_lines.append(
            f"{i}. *{title_safe}* ({h.platform} {mode_icon})\n"
            f"   💰 Prize: `{prize}`\n"
            f"   🔗 [Click to Apply / View Details]({h.url})\n"
        )

    if len(hackathons) > max_items:
        message_lines.append(f"\n_...and {len(hackathons) - max_items} more hackathons available!_")

    text = "\n".join(message_lines)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(url, json={
            "chat_id": chat,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }, timeout=10)
        return res.status_code == 200
    except Exception as e:
        logger.error(f"Telegram notification error: {e}")
        return False

def send_discord_webhook(
    hackathons: List[Hackathon],
    webhook_url: Optional[str] = None,
    max_items: int = 6
) -> bool:
    """
    Sends latest hackathon links to a Discord channel via free incoming webhook.
    Requires DISCORD_WEBHOOK_URL (or passed as argument).
    """
    hook = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not hook:
        logger.warning("Discord Webhook URL not configured.")
        return False

    if not hackathons:
        return False

    embeds = []
    for h in hackathons[:max_items]:
        embed = {
            "title": f"🚀 {h.title}",
            "url": h.url,
            "description": h.description[:200] if h.description else f"Explore {h.title} on {h.platform}",
            "color": 0x38bdf8 if h.is_online else 0x10b981,
            "fields": [
                {"name": "Platform", "value": h.platform, "inline": True},
                {"name": "Prize Pool", "value": h.prize_pool or "Prizes & Mentorship", "inline": True},
                {"name": "Type", "value": "🇮🇳 India" if h.is_india else "🌐 Global Online", "inline": True},
            ],
            "footer": {"text": f"Status: {h.status} • Mode: {h.location or 'Online'}"}
        }
        if h.thumbnail:
            embed["thumbnail"] = {"url": h.thumbnail}
        embeds.append(embed)

    payload = {
        "username": "Hackathon Hunter Bot",
        "avatar_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=100&auto=format&fit=crop&q=60",
        "content": f"🎯 **New Hackathon Opportunities Alert!** Found **{len(hackathons)}** live hackathons.",
        "embeds": embeds
    }

    try:
        res = requests.post(hook, json=payload, timeout=10)
        return res.status_code in [200, 204]
    except Exception as e:
        logger.error(f"Discord webhook error: {e}")
        return False
