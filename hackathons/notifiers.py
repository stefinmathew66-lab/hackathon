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
    Sends latest hackathon links to a Telegram channel or group for BROADCASTING.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (or channel username @my_channel).
    """
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat:
        logger.warning("Telegram Bot Token or Chat ID not configured.")
        return False

    if not hackathons:
        return False

    message_lines = [
        "📢 *HACKATHON BROADCAST: LATEST OPPORTUNITIES* 🚀\n",
        f"Found *{len(hackathons)}* active hackathons matching your criteria:\n"
    ]

    for i, h in enumerate(hackathons[:max_items], 1):
        mode_icon = "🇮🇳" if h.is_india else "🌐"
        prize = h.prize_pool or "Swag & Prizes"
        title_safe = h.title.replace("*", "").replace("_", "").replace("[", "").replace("]", "")
        message_lines.append(
            f"{i}. *{title_safe}* ({h.platform} {mode_icon})\n"
            f"   💰 Prize: `{prize}`\n"
            f"   🔗 [Apply / View Details]({h.url})\n"
        )

    if len(hackathons) > max_items:
        message_lines.append(f"\n_...and {len(hackathons) - max_items} more hackathons live!_")

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

def send_whatsapp_alert(
    hackathons: List[Hackathon],
    phone_number: Optional[str] = None,
    api_key: Optional[str] = None,
    max_items: int = 6
) -> bool:
    """
    Sends latest hackathons directly to your PERSONAL WhatsApp for 100% free via CallMeBot API.
    Requires WHATSAPP_PHONE (e.g. +919876543210) and WHATSAPP_APIKEY.
    """
    phone = phone_number or os.getenv("WHATSAPP_PHONE")
    key = api_key or os.getenv("WHATSAPP_APIKEY")
    
    if not phone or not key:
        logger.warning("WhatsApp Phone or API Key not configured.")
        return False

    if not hackathons:
        return False

    clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "").strip()

    message_lines = [
        "🚀 *DAILY HACKATHONS DIGEST (8:00 AM)* 🚀\n",
        f"Good morning! Found *{len(hackathons)}* latest hackathons for you:\n"
    ]

    for i, h in enumerate(hackathons[:max_items], 1):
        mode_icon = "🇮🇳" if h.is_india else "🌐"
        prize = h.prize_pool or "Swag & Prizes"
        title_safe = h.title.replace("*", "").replace("_", "")
        message_lines.append(
            f"{i}. *{title_safe}* ({h.platform} {mode_icon})\n"
            f"   💰 Prize: {prize}\n"
            f"   🔗 {h.url}\n"
        )

    if len(hackathons) > max_items:
        message_lines.append(f"\n_...and {len(hackathons) - max_items} more hackathons available!_")

    message_text = "\n".join(message_lines)
    
    url = "https://api.callmebot.com/whatsapp.php"
    params = {
        "phone": clean_phone,
        "text": message_text,
        "apikey": key
    }

    try:
        res = requests.get(url, params=params, timeout=15)
        return res.status_code == 200 and "error" not in res.text.lower()
    except Exception as e:
        logger.error(f"WhatsApp notification error: {e}")
        return False

def send_discord_webhook(
    hackathons: List[Hackathon],
    webhook_url: Optional[str] = None,
    max_items: int = 6
) -> bool:
    """
    Sends latest hackathon links to a Discord channel via free incoming webhook.
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
