import logging
import urllib.parse
from html.parser import HTMLParser
from typing import List, Tuple
import requests
from ..models import Hackathon

logger = logging.getLogger(__name__)

class MLHAnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: List[Tuple[str, str]] = []
        self._current_href = None
        self._current_text: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            self._current_href = attrs_dict.get("href")
            self._current_text = []

    def handle_data(self, data):
        if self._current_href:
            self._current_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._current_href:
            text = "".join(self._current_text).strip()
            self.links.append((self._current_href, text))
            self._current_href = None
            self._current_text = []

def fetch_mlh_hackathons() -> List[Hackathon]:
    """
    Fetches global student & digital hackathons from MLH (Major League Hacking).
    Uses Python's standard library HTML parser (zero external dependencies).
    """
    hackathons: List[Hackathon] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    
    urls = [
        "https://www.mlh.com/seasons/2026/events",
        "https://www.mlh.com/seasons/2027/events",
        "https://mlh.io/events"
    ]
    
    seen_urls = set()
    
    for page_url in urls:
        try:
            response = requests.get(page_url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
                
            parser = MLHAnchorParser()
            parser.feed(response.text)
            
            for href, text in parser.links:
                if not href or not href.startswith("http"):
                    continue
                if any(x in href for x in ["twitter.com", "facebook.com", "instagram.com", "github.com", "youtube.com", "mlh.com", "mlh.io", "discord.gg", "twitch.tv"]):
                    continue
                    
                parsed_url = urllib.parse.urlparse(href)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                title = ""
                if "utm_content" in query_params:
                    title = query_params["utm_content"][0].replace("+", " ")
                if not title:
                    title = text
                if not title or len(title) < 3 or title.lower() in ["apply now", "register", "website", "details", "link"]:
                    continue
                    
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if clean_url in seen_urls:
                    continue
                seen_urls.add(clean_url)
                
                is_india = any(w in title.lower() for w in ["india", "prix", "delhi", "mumbai", "bengaluru", "hackprix", "hacknit", "hackiiit"])
                is_online = True
                
                tags = ["MLH", "Student", "Global"]
                if is_india:
                    tags.append("India")
                if is_online:
                    tags.append("Online")

                hackathons.append(Hackathon(
                    id=f"mlh_{abs(hash(clean_url))}",
                    title=title,
                    url=href,
                    platform="MLH",
                    description=f"Official MLH Member Hackathon: {title}. Build projects, learn from mentors, and compete for global prizes.",
                    is_india=is_india,
                    is_online=is_online,
                    prize_pool="Sponsor Bounties, Swag & Hardware",
                    location="Online / Hybrid",
                    tags=tags,
                    thumbnail="https://static.mlh.io/brand-assets/logo/official/mlh-logo-color.png",
                    status="Upcoming"
                ))
        except Exception as e:
            logger.error(f"Error fetching MLH from {page_url}: {e}")
            
    return hackathons
