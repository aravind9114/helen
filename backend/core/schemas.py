from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SegmentRequest(BaseModel):
    image_path: str
    mode: str = "point"  # point, box
    points: Optional[List[List[int]]] = None
    box: Optional[List[int]] = None
    x: Optional[int] = None  # Legacy support
    y: Optional[int] = None  # Legacy support

class InpaintRequest(BaseModel):
    image_path: str
    mask_path: str
    prompt: str
    strength: float = 1.0  # Default to max strength for replacement
    guidance_scale: float = 10.0

class RecolorRequest(BaseModel):
    image_path: str
    mask_path: str
    color_hex: str

class GenerateRequest(BaseModel):
    image_path: str
    room_type: str
    style: str
    budget: int
    provider: str = "offline"

class PlanRequest(BaseModel):
    user_request: str
    detected_items: Optional[List[Dict[str, Any]]] = None # Changed to list of dicts for details
    budget: int = 10000 # Default budget
