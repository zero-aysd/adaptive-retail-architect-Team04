# agents/market_analyst.py
from app.tools.run_market_analyst import run_market_analyst
from app.agents.geo_resolver import resolve_geo
from pydantic import BaseModel, Field

from pydantic import BaseModel, Field
from typing import List, Dict

class MarketInput(BaseModel):
    """
    Input schema for the market analyst tool.

    Attributes:
        city (str): Name of the city to analyze market trends for.
        keywords (List[str], optional): List of keywords to focus the analysis on.
            Defaults to ["iPhone 15", "gaming laptop"].
    """
    city: str
    keywords: List[str] = Field(default=["iPhone 15", "gaming laptop"])


def market_analyst_tool(input: MarketInput) -> Dict:
    """
    Executes a market analysis based on the provided city and keywords.

    Steps:
        1. Resolves geographic information for the specified city.
        2. Runs the market analyst analysis using the resolved geo information 
           and input keywords.
        3. Returns the analysis results as a dictionary.

    Args:
        input (MarketInput): Input object containing the city and keywords.

    Returns:
        dict: Dictionary containing market analysis results such as 
              trends over time, interest scores, and related metrics.
    """
    geo = resolve_geo(input.city)
    result = run_market_analyst(
        keywords=input.keywords,
        geo=geo["geo"],
        sub_geo=geo["sub_geo"],
        
    )
    return result