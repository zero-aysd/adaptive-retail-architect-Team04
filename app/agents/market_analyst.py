from langchain.tools import tool
from pytrends.request import TrendReq  # For real-time Google Trends
from typing_extensions import List, Dict,Any
import os

@tool
def get_local_trends(city: str, keywords: List[str] = ["electronics"]) -> Dict[str, Any]:
    """
    Fetch real-time trending products for a city using Google Trends.
    """
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        # Mock for now; replace with real API call
        trends = {
            "city": city,
            "top_trends": [f"{kw} in {city}" for kw in keywords],
            "interest_over_time": {"smartphones": 85, "laptops": 72},
            "related_queries": ["wireless earbuds", "gaming laptops"]
        }
        return trends
    except Exception as e:
        return {"error": str(e), "fallback": "Using default trends for electronics"}