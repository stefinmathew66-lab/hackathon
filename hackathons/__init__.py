"""
Hackathon Aggregator and Link Fetcher Module.
Zero-cost, multi-source hackathon crawler & bot for India and Global Online hackathons.
"""
from .models import Hackathon
from .aggregator import HackathonAggregator

__all__ = ["Hackathon", "HackathonAggregator"]
