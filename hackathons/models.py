import re
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Hackathon(BaseModel):
    id: str
    title: str
    url: str
    platform: str
    description: Optional[str] = ""
    is_india: bool = False
    is_online: bool = True
    city: Optional[str] = "Online"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    deadline: Optional[str] = None
    prize_pool: Optional[str] = None
    prize_usd_approx: Optional[float] = 0.0
    category: str = "Open Innovation"  # AI/ML, Web3, Mobile, Student, Hiring, Gaming, Security, Open
    location: Optional[str] = "Online"
    tags: List[str] = Field(default_factory=list)
    thumbnail: Optional[str] = None
    status: str = "Upcoming"  # Upcoming, Ongoing, Closed
    fetched_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def compute_fields(self):
        """Auto-computes category, city, and prize approximation for enhanced filtering"""
        title_desc = (self.title + " " + (self.description or "") + " " + " ".join(self.tags)).lower()
        
        # Determine Category
        if any(w in title_desc for w in ["ai", "machine learning", "llm", "gpt", "agent", "deep learning", "neural", "vision"]):
            self.category = "AI & ML"
        elif any(w in title_desc for w in ["web3", "blockchain", "crypto", "solana", "ethereum", "eth", "nft", "defi", "smart contract"]):
            self.category = "Web3 & Crypto"
        elif any(w in title_desc for w in ["game", "gaming", "unreal", "unity", "xr", "ar", "vr", "metaverse"]):
            self.category = "Gaming & AR/VR"
        elif any(w in title_desc for w in ["cyber", "security", "cloud", "devops", "aws", "docker", "kubernetes"]):
            self.category = "Cyber & Cloud"
        elif any(w in title_desc for w in ["hiring", "job", "internship", "placement", "interview", "recruitment"]):
            self.category = "Hiring & Careers"
        elif any(w in title_desc for w in ["student", "college", "university", "campus", "school", "freshers", "beginner"]):
            self.category = "Students & Colleges"
        elif any(w in title_desc for w in ["app", "mobile", "ios", "android", "flutter", "react", "fullstack"]):
            self.category = "Mobile & Web Dev"
        else:
            self.category = "Open Innovation"

        # Detect City in India if applicable
        loc_lower = (self.location or "").lower()
        if "bengaluru" in loc_lower or "bangalore" in loc_lower:
            self.city = "Bengaluru"
        elif "delhi" in loc_lower or "noida" in loc_lower or "gurgaon" in loc_lower or "ghaziabad" in loc_lower:
            self.city = "Delhi-NCR"
        elif "mumbai" in loc_lower or "navi mumbai" in loc_lower or "thane" in loc_lower:
            self.city = "Mumbai"
        elif "kolkata" in loc_lower:
            self.city = "Kolkata"
        elif "chennai" in loc_lower:
            self.city = "Chennai"
        elif "hyderabad" in loc_lower:
            self.city = "Hyderabad"
        elif "pune" in loc_lower:
            self.city = "Pune"
        elif self.is_online:
            self.city = "Online (Virtual)"
        elif self.is_india:
            self.city = "Other India"
        else:
            self.city = "International"

        # Parse Prize Approximate Value in USD / INR
        if self.prize_pool:
            clean_p = self.prize_pool.replace(",", "").replace("$", "").replace("₹", "")
            numbers = re.findall(r"\d+", clean_p)
            if numbers:
                val = float(numbers[0])
                if "$" in self.prize_pool:
                    self.prize_usd_approx = val
                elif "₹" in self.prize_pool or "INR" in self.prize_pool or "rupee" in self.prize_pool.lower():
                    self.prize_usd_approx = val / 85.0  # Approx USD conversion
                else:
                    self.prize_usd_approx = val

    def to_dict(self):
        self.compute_fields()
        return self.model_dump()
