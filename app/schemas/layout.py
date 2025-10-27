# schemas/layout.py
from pydantic import BaseModel, Field
from typing import List, Literal

class Zone(BaseModel):
    name: str
    x: float
    y: float
    width: float
    height: float
    fixtures: List[str] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)

class LayoutPlan(BaseModel):
    store_name: str
    city: str
    dimensions_m: tuple[float, float]
    entrance_side: Literal["north", "south", "east", "west"]
    zones: List[Zone]
    compliance_notes: List[str] = Field(default_factory=list)
    best_practice_score: float = Field(ge=0, le=10)