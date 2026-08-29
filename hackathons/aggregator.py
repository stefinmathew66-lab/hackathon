import csv
import io
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any

from .models import Hackathon
from .fetchers import (
    fetch_devfolio_hackathons,
    fetch_unstop_hackathons,
    fetch_devpost_hackathons,
    fetch_hackerearth_hackathons,
    fetch_mlh_hackathons,
)

logger = logging.getLogger(__name__)

class HackathonAggregator:
    def __init__(self, cache_ttl_seconds: int = 300):
        self._cache: List[Hackathon] = []
        self._last_fetched: float = 0
        self._cache_ttl = cache_ttl_seconds

    def fetch_all(self, force_refresh: bool = False) -> List[Hackathon]:
        """
        Concurrently fetches hackathons from all platforms with caching and deduplication.
        """
        now = time.time()
        if not force_refresh and self._cache and (now - self._last_fetched < self._cache_ttl):
            return self._cache

        all_hackathons: List[Hackathon] = []
        fetch_tasks = {
            "Devfolio": lambda: fetch_devfolio_hackathons(limit=30),
            "Unstop": lambda: fetch_unstop_hackathons(per_page=30),
            "Devpost": lambda: fetch_devpost_hackathons(pages=2),
            "HackerEarth": fetch_hackerearth_hackathons,
            "MLH": fetch_mlh_hackathons,
        }

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_platform = {executor.submit(fn): name for name, fn in fetch_tasks.items()}
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    results = future.result()
                    all_hackathons.extend(results)
                    logger.info(f"Fetched {len(results)} hackathons from {platform}")
                except Exception as e:
                    logger.error(f"Failed to fetch from {platform}: {e}")

        # Deduplicate
        deduped: List[Hackathon] = []
        seen_titles = set()
        seen_urls = set()

        for h in all_hackathons:
            clean_title = "".join(filter(str.isalnum, h.title.lower()))
            clean_url = h.url.split("?")[0].rstrip("/")
            
            if clean_title in seen_titles or clean_url in seen_urls:
                continue
            seen_titles.add(clean_title)
            seen_urls.add(clean_url)
            h.compute_fields()
            deduped.append(h)

        self._cache = deduped
        self._last_fetched = now
        return self._cache

    def filter(
        self,
        india_only: Optional[bool] = None,
        online_only: Optional[bool] = None,
        platform: Optional[str] = None,
        category: Optional[str] = None,
        city: Optional[str] = None,
        min_prize_usd: Optional[float] = None,
        query: Optional[str] = None,
        status: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[Hackathon]:
        """
        Filters hackathons based on criteria.
        """
        hackathons = self.fetch_all(force_refresh=force_refresh)
        filtered = hackathons

        if india_only is True:
            filtered = [h for h in filtered if h.is_india]
        elif india_only is False:
            filtered = [h for h in filtered if not h.is_india]

        if online_only is True:
            filtered = [h for h in filtered if h.is_online]

        if platform and platform.lower() != "all":
            filtered = [h for h in filtered if h.platform.lower() == platform.lower()]

        if category and category.lower() != "all":
            filtered = [h for h in filtered if h.category.lower() == category.lower()]

        if city and city.lower() != "all":
            filtered = [h for h in filtered if h.city.lower() == city.lower()]

        if min_prize_usd is not None and min_prize_usd > 0:
            filtered = [h for h in filtered if (h.prize_usd_approx or 0) >= min_prize_usd]

        if status and status.lower() != "all":
            filtered = [h for h in filtered if h.status.lower() == status.lower()]


        if query:
            q = query.lower().strip()
            filtered = [
                h for h in filtered
                if q in h.title.lower()
                or q in (h.description or "").lower()
                or q in (h.location or "").lower()
                or any(q in t.lower() for t in h.tags)
                or q in (h.prize_pool or "").lower()
            ]

        return filtered

    def get_stats(self) -> Dict[str, Any]:
        hackathons = self.fetch_all()
        platforms: Dict[str, int] = {}
        for h in hackathons:
            platforms[h.platform] = platforms.get(h.platform, 0) + 1

        return {
            "total": len(hackathons),
            "india_total": len([h for h in hackathons if h.is_india]),
            "global_online_total": len([h for h in hackathons if h.is_online and not h.is_india]),
            "online_total": len([h for h in hackathons if h.is_online]),
            "platforms": platforms,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(self._last_fetched)) if self._last_fetched else "Never"
        }

    def export_json(self, hackathons: Optional[List[Hackathon]] = None) -> str:
        items = hackathons if hackathons is not None else self.fetch_all()
        return json.dumps([h.to_dict() for h in items], indent=2)

    def export_csv(self, hackathons: Optional[List[Hackathon]] = None) -> str:
        items = hackathons if hackathons is not None else self.fetch_all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Title", "Platform", "URL", "Location", "Online", "India", "Prize Pool", "Status", "Tags"])
        for h in items:
            writer.writerow([
                h.title,
                h.platform,
                h.url,
                h.location or "",
                "Yes" if h.is_online else "No",
                "Yes" if h.is_india else "No",
                h.prize_pool or "N/A",
                h.status,
                ", ".join(h.tags)
            ])
        return output.getvalue()

    def export_markdown(self, hackathons: Optional[List[Hackathon]] = None) -> str:
        items = hackathons if hackathons is not None else self.fetch_all()
        lines = [
            "# 🚀 Latest Hackathons (India & Global Online)",
            f"\n*Total Opportunities Found: {len(items)}*\n",
            "| Platform | Hackathon Title | Location / Mode | Prize Pool | Direct Apply Link |",
            "|---|---|---|---|---|"
        ]
        for h in items:
            mode = "🌐 Online" if h.is_online else (h.location or "In-Person")
            if h.is_india:
                mode += " 🇮🇳"
            title_escaped = h.title.replace("|", "-")
            prize_escaped = (h.prize_pool or "Swag & Prizes").replace("|", "-")
            lines.append(f"| **{h.platform}** | {title_escaped} | {mode} | {prize_escaped} | [Apply / View]({h.url}) |")

        return "\n".join(lines)
