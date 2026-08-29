import os
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from hackathons.aggregator import HackathonAggregator
from hackathons.notifiers import send_telegram_alert, send_discord_webhook

app = FastAPI(
    title="Hackathon Hunter API",
    description="100% Free Hackathon Link Fetcher & Aggregator API (India & Global Online)",
    version="1.0.0"
)

aggregator = HackathonAggregator(cache_ttl_seconds=300)

# Notification Request Models
class TelegramAlertRequest(BaseModel):
    token: Optional[str] = None
    chat_id: Optional[str] = None
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
    q: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Status filter"),
    refresh: bool = Query(False, description="Force refresh cache")
):
    results = aggregator.filter(
        india_only=india_only,
        online_only=online_only,
        platform=platform,
        query=q,
        status=status,
        force_refresh=refresh
    )
    return {
        "count": len(results),
        "hackathons": [h.to_dict() for h in results]
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
    q: Optional[str] = None
):
    items = aggregator.filter(india_only=india_only, online_only=online_only, platform=platform, query=q)
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
        raise HTTPException(status_code=400, detail="Failed to send Telegram alert. Check bot token and chat ID.")
    return {"status": "success", "message": f"Sent {len(items)} hackathons to Telegram!"}

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
