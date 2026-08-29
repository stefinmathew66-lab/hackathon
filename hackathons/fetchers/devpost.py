import logging
import re
from typing import List
import requests
from ..models import Hackathon

logger = logging.getLogger(__name__)

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    clean = re.sub(r"<.*?>", "", str(raw_html))
    return clean.strip()

def fetch_devpost_hackathons(pages: int = 2) -> List[Hackathon]:
    """
    Fetches global online & in-person hackathons from Devpost's public API.
    """
    hackathons: List[Hackathon] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    seen_ids = set()
    
    for page in range(1, pages + 1):
        url = f"https://devpost.com/api/hackathons?challenge_type[]=online&status[]=upcoming&status[]=open&page={page}"
        try:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code != 200:
                logger.warning(f"Devpost returned status {response.status_code} for page {page}")
                continue
                
            data = response.json()
            items = data.get("hackathons", [])
            
            for item in items:
                item_id = str(item.get("id"))
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                
                title = item.get("title") or "Devpost Hackathon"
                event_url = item.get("url") or f"https://devpost.com/hackathons/{item_id}"
                
                # Check location
                displayed_loc = item.get("displayed_location", {}) or {}
                location_text = displayed_loc.get("location", "Online") if isinstance(displayed_loc, dict) else "Online"
                
                is_online = "online" in location_text.lower() or displayed_loc.get("icon") == "globe"
                is_india = "india" in location_text.lower()
                
                # Prizes
                prize_amount = clean_html(item.get("prize_amount", ""))
                prize_pool = prize_amount if prize_amount else "Swag & Recognitions"
                
                # Themes / Tags
                themes = [t.get("name") for t in item.get("themes", []) if isinstance(t, dict) and t.get("name")]
                tags = ["Devpost", "Global"] + themes[:3]
                if is_online:
                    tags.append("Online")
                if is_india:
                    tags.append("India")

                # Thumbnail
                thumb = item.get("thumbnail_url")
                if thumb and thumb.startswith("//"):
                    thumb = f"https:{thumb}"
                    
                dates_str = item.get("submission_period_dates") or item.get("time_left_to_submission")
                org_name = item.get("organization_name") or "Devpost Community"
                
                hackathons.append(Hackathon(
                    id=f"devpost_{item_id}",
                    title=title,
                    url=event_url,
                    platform="Devpost",
                    description=f"Hosted by {org_name}. Submission period: {dates_str}.",
                    is_india=is_india,
                    is_online=is_online,
                    start_date=dates_str,
                    prize_pool=prize_pool,
                    location=location_text,
                    tags=tags,
                    thumbnail=thumb,
                    status="Upcoming" if item.get("open_state") == "upcoming" else "Ongoing"
                ))
        except Exception as e:
            logger.error(f"Error fetching from Devpost page {page}: {e}")
            
    return hackathons
