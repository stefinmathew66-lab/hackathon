import logging
from typing import List
import requests
from ..models import Hackathon

logger = logging.getLogger(__name__)

def fetch_unstop_hackathons(per_page: int = 40) -> List[Hackathon]:
    """
    Fetches hackathons from Unstop (formerly Dare2Compete),
    India's leading student, college, and corporate hackathon platform.
    """
    hackathons: List[Hackathon] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    
    urls = [
        f"https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&per_page={per_page}",
        f"https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&sub_type=online&per_page={per_page}"
    ]
    
    seen_ids = set()
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code != 200:
                continue
                
            data = response.json()
            items = data.get("data", {}).get("data", []) if isinstance(data.get("data"), dict) else []
            
            for item in items:
                item_id = str(item.get("id"))
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                
                title = item.get("title") or "Unstop Hackathon"
                seo_url = item.get("public_url") or item.get("seo_url")
                if seo_url and not seo_url.startswith("http"):
                    event_url = f"https://unstop.com/{seo_url}"
                elif seo_url:
                    event_url = seo_url
                else:
                    event_url = f"https://unstop.com/hackathons/{item_id}"
                
                sub_type = str(item.get("sub_type", "")).lower()
                is_online = "online" in sub_type or item.get("region") == "online"
                
                org = item.get("organisation", {}) or {}
                org_name = org.get("name") if isinstance(org, dict) else ""
                
                banner = item.get("banner_mobile", {}).get("url") if isinstance(item.get("banner_mobile"), dict) else None
                if not banner and isinstance(item.get("banner_web"), dict):
                    banner = item.get("banner_web", {}).get("url")
                if not banner and isinstance(item.get("logo"), dict):
                    banner = item.get("logo", {}).get("url")
                    
                # Extract Prize Pool
                prizes = item.get("prizes", [])
                prize_str = "Certificates & Mentorship"
                if prizes and isinstance(prizes, list):
                    first_prize = prizes[0]
                    cash = first_prize.get("cash")
                    if cash:
                        currency = "₹" if "rupee" in str(first_prize.get("currency", "")).lower() else "$"
                        prize_str = f"{currency}{int(cash):,}"
                        
                start_date = item.get("start_date") or item.get("regn_start_date")
                end_date = item.get("end_date") or item.get("regn_end_date")
                
                tags = ["Unstop", "Hackathon"]
                if org_name:
                    tags.append(org_name[:20])
                if is_online:
                    tags.append("Online")
                tags.append("India")

                hackathons.append(Hackathon(
                    id=f"unstop_{item_id}",
                    title=title,
                    url=event_url,
                    platform="Unstop",
                    description=item.get("short_desc") or f"Organized by {org_name or 'Unstop'}. Register to participate and win prizes.",
                    is_india=True,
                    is_online=is_online,
                    start_date=start_date,
                    end_date=end_date,
                    prize_pool=prize_str,
                    location="Online" if is_online else (org_name or "India"),
                    tags=tags,
                    thumbnail=banner,
                    status="Upcoming" if item.get("status") != "closed" else "Closed"
                ))
        except Exception as e:
            logger.error(f"Error fetching from Unstop ({url}): {e}")
            
    return hackathons
