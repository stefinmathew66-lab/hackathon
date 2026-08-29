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
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    deadline: Optional[str] = None
    prize_pool: Optional[str] = None
    location: Optional[str] = "Online"
    tags: List[str] = Field(default_factory=list)
    thumbnail: Optional[str] = None
    status: str = "Upcoming"  # Upcoming, Ongoing, Closed
    fetched_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return self.model_dump()
