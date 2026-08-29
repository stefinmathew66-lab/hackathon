import logging
import ast
import json
from typing import List
import requests
from ..models import Hackathon

logger = logging.getLogger(__name__)

def fetch_hackerearth_hackathons() -> List[Hackathon]:
    """
    Fetches upcoming and ongoing hackathons from HackerEarth's public events API.
    """
    hackathons: List[Hackathon] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    
    url = "https://www.hackerearth.com/api/events/upcoming/?format=json"
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code != 200:
            logger.warning(f"HackerEarth returned status {response.status_code}")
            return []
            
        # HackerEarth returns single-quote JSON string
        raw_text = response.text
        try:
            data = ast.literal_eval(json.loads(raw_text))
        except Exception:
            try:
                data = json.loads(raw_text)
            except Exception:
                data = {}
                
        events = data.get("response", []) if isinstance(data, dict) else []
        
        for ev in events:
            title = ev.get("title") or "HackerEarth Challenge"
            event_url = ev.get("url") or ev.get("subscribe")
            if not event_url:
                continue
                
            challenge_type = ev.get("challenge_type") or "Hackathon"
            description = ev.get("description") or f"Join {title} on HackerEarth."
            status = str(ev.get("status", "UPCOMING")).capitalize()
            start_date = ev.get("start_utc_tz") or ev.get("date")
            end_date = ev.get("end_utc_tz")
            
            # HackerEarth challenges are developer focused and mostly online
            is_online = True
            is_india = True  # HackerEarth has strong presence and community in India
            
            tags = ["HackerEarth", challenge_type, "Developer", "Online", "India"]

            hackathons.append(Hackathon(
                id=f"he_{abs(hash(event_url))}",
                title=title,
                url=event_url,
                platform="HackerEarth",
                description=description[:250],
                is_india=is_india,
                is_online=is_online,
                start_date=str(start_date) if start_date else None,
                end_date=str(end_date) if end_date else None,
                prize_pool="Cash Prizes & Hiring",
                location="Online",
                tags=tags,
                thumbnail=ev.get("thumbnail"),
                status=status if status in ["Upcoming", "Ongoing"] else "Upcoming"
            ))
    except Exception as e:
        logger.error(f"Error fetching from HackerEarth: {e}")
        
    return hackathons
