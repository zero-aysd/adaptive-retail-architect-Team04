from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LayoutRequest(BaseModel):
    """Request model for retail layout generation"""
    city: str  # e.g., "Surat"
    store_area: Optional[float] = 500.0  # sqm
    constraints: Optional[List[str]] = None  # e.g., ["no permanent fixtures on northern wall"]
    design_focus: Optional[str] = "optimize customer flow"
    target_products: Optional[List[str]] = None  # e.g., ["smartphones", "laptops"]

class LayoutResponse(BaseModel):
    """Response model for layout generation"""
    success: bool
    layout_id: str
    layout_data: Dict[str, Any]  # JSON plan from Layout Strategist
    diagram_url: Optional[str] = None  # URL to 2D PNG
    trends_summary: Dict[str, Any]  # From Market Analyst
    render_time: float
    generated_at: datetime
    metadata: Dict[str, Any] = {}

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    error_code: str
    timestamp: datetime