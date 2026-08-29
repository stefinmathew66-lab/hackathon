import logging
from typing import List
import requests
from ..models import Hackathon

logger = logging.getLogger(__name__)

def fetch_devfolio_hackathons(limit: int = 40) -> List[Hackathon]:
    """
    Fetches hackathons from Devfolio's open public API.
    Devfolio hosts top hackathons in India and globally.
    """
    hackathons: List[Hackathon] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    url = f"https://api.devfolio.co/api/hackathons?filter=all&page=1&limit={limit}"
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code != 200:
            logger.warning(f"Devfolio returned status {response.status_code}")
            return []
        
        data = response.json()
        items = data.get("result", [])
        
        for item in items:
            name = item.get("name") or "Devfolio Hackathon"
            slug = item.get("slug")
            subdomain = item.get("subdomain")
            
            # Devfolio hackathon URL
            if subdomain:
                event_url = f"https://{subdomain}.devfolio.co"
            elif slug:
                event_url = f"https://devfolio.co/hackathons/{slug}"
            else:
                event_url = "https://devfolio.co"
                
            setting = item.get("hackathon_setting") or {}
            logo = setting.get("logo") or item.get("hero_image") or item.get("logo")
            
            # Devfolio hackathons are primarily based in India with global virtual participation
            is_online = item.get("is_online", True)
            location = item.get("location") or ("Online" if is_online else "India (In-Person/Hybrid)")
            
            # Check if India
            is_india = True  # Devfolio's core ecosystem is India-centric
            if location and any(c in location.lower() for c in ["usa", "singapore", "london", "canada", "europe"]):
                is_india = False
            if "india" in location.lower() or "delhi" in location.lower() or "bengaluru" in location.lower() or "bangalore" in location.lower() or "mumbai" in location.lower():
                is_india = True

            start_date = setting.get("reg_starts_at") or item.get("starts_at")
            end_date = setting.get("reg_ends_at") or item.get("ends_at")
            
            prizes_val = item.get("prizes_total") or item.get("prize_amount") or "Prizes & Swag"
            prize_pool = f"₹{prizes_val:,}" if isinstance(prizes_val, (int, float)) and prizes_val > 0 else str(prizes_val)

            tags = ["Devfolio", "Web3" if "web3" in name.lower() or "eth" in name.lower() else "Tech"]
            if is_online:
                tags.append("Online")
            if is_india:
                tags.append("India")

            hackathons.append(Hackathon(
                id=f"devfolio_{item.get('id') or subdomain or slug or hash(event_url)}",
                title=name,
                url=event_url,
                platform="Devfolio",
                description=item.get("tagline") or f"Explore and build at {name} on Devfolio.",
                is_india=is_india,
                is_online=is_online,
                start_date=start_date,
                end_date=end_date,
                prize_pool=prize_pool,
                location=location,
                tags=tags,
                thumbnail=logo,
                status="Upcoming" if item.get("is_open", True) else "Ongoing"
            ))
            
    except Exception as e:
        logger.error(f"Error fetching from Devfolio: {e}")
        
    return hackathons
