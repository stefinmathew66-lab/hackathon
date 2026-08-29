import os
import threading
import time
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from hackathons.aggregator import HackathonAggregator
from hackathons.notifiers import send_telegram_alert, send_whatsapp_alert, send_discord_webhook

app = FastAPI(
    title="Hackathon Hunter API",
    description="100% Free Hackathon Link Fetcher & Aggregator API (India & Global Online)",
    version="2.0.0"
)

aggregator = HackathonAggregator(cache_ttl_seconds=300)

# Automatic background refresh worker (refreshes live opportunities in background every 6 hours)
def background_refresh_worker():
    while True:
        try:
            aggregator.fetch_all(force_refresh=True)
        except Exception:
            pass
        time.sleep(21600)  # 6 hours

@app.on_event("startup")
def startup_event():
    # Start auto-refresh daemon thread
    t = threading.Thread(target=background_refresh_worker, daemon=True)
    t.start()

# Notification Request Models
class TelegramAlertRequest(BaseModel):
    token: Optional[str] = None
    chat_id: Optional[str] = None
    india_only: Optional[bool] = None
    online_only: Optional[bool] = None

class WhatsAppAlertRequest(BaseModel):
    phone: Optional[str] = None
    apikey: Optional[str] = None
    india_only: Optional[bool] = None
    online_only: Optional[bool] = None

class DiscordAlertRequest(BaseModel):
    webhook_url: Optional[str] = None
    india_only: Optional[bool] = None
    online_only: Optional[bool] = None

@app.get("/api/hackathons")
def get_hackathons(
    india_only: Optional[bool] = Query(None, description="Filter India hackathons"),
    online_only: Optional[bool] = Query(None, description="Filter online hackathons"),
    platform: Optional[str] = Query(None, description="Platform name"),
    category: Optional[str] = Query(None, description="Category track"),
    city: Optional[str] = Query(None, description="City location"),
    min_prize: Optional[float] = Query(None, description="Minimum prize pool USD"),
    q: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Status filter"),
    refresh: bool = Query(False, description="Force refresh cache")
):
    results = aggregator.filter(
        india_only=india_only,
        online_only=online_only,
        platform=platform,
        category=category,
        city=city,
        min_prize_usd=min_prize,
        query=q,
        status=status,
        force_refresh=refresh
    )
    return {
        "count": len(results),
        "hackathons": [h.to_dict() for h in results],
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(aggregator._last_fetched)) if aggregator._last_fetched else "Live"
    }

@app.get("/api/stats")
def get_stats():
    return aggregator.get_stats()

@app.get("/api/export")
def export_hackathons(
    format: str = Query("json", enum=["json", "csv", "markdown"]),
    india_only: Optional[bool] = None,
    online_only: Optional[bool] = None,
    platform: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    q: Optional[str] = None
):
    items = aggregator.filter(
        india_only=india_only,
        online_only=online_only,
        platform=platform,
        category=category,
        city=city,
        query=q
    )
    if format == "csv":
        content = aggregator.export_csv(items)
        return Response(content=content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=hackathons.csv"})
    elif format == "markdown":
        content = aggregator.export_markdown(items)
        return Response(content=content, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=hackathons.md"})
    else:
        content = aggregator.export_json(items)
        return Response(content=content, media_type="application/json", headers={"Content-Disposition": "attachment; filename=hackathons.json"})

@app.post("/api/notify/telegram")
def trigger_telegram_alert(req: TelegramAlertRequest):
    items = aggregator.filter(india_only=req.india_only, online_only=req.online_only)
    success = send_telegram_alert(items, bot_token=req.token, chat_id=req.chat_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to broadcast to Telegram. Check bot token and chat/channel ID.")
    return {"status": "success", "message": f"Broadcasted {len(items)} hackathons to Telegram channel!"}

@app.post("/api/notify/whatsapp")
def trigger_whatsapp_alert(req: WhatsAppAlertRequest):
    items = aggregator.filter(india_only=req.india_only, online_only=req.online_only)
    success = send_whatsapp_alert(items, phone_number=req.phone, api_key=req.apikey)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to send WhatsApp message. Check phone number and CallMeBot API key.")
    return {"status": "success", "message": f"Sent personal hackathon digest to WhatsApp!"}

@app.post("/api/notify/discord")
def trigger_discord_alert(req: DiscordAlertRequest):
    items = aggregator.filter(india_only=req.india_only, online_only=req.online_only)
    success = send_discord_webhook(items, webhook_url=req.webhook_url)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to send Discord alert. Check webhook URL.")
    return {"status": "success", "message": f"Sent {len(items)} hackathons to Discord!"}

# Serve static dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_home():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Hackathon Hunter Web Dashboard at http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
