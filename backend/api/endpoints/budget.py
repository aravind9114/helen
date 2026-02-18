from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.core.budget_engine import budget_engine
from backend.services.logging import logger

router = APIRouter()

class CalculateRequest(BaseModel):
    plan_steps: List[Dict[str, Any]]

@router.post("/api/budget/calculate")
async def calculate_cost(request: CalculateRequest):
    """Calculate cost for a plan."""
    try:
        return budget_engine.calculate_plan_cost(request.plan_steps)
    except Exception as e:
        logger.error(f"Failed to calculate cost: {e}")
        raise HTTPException(500, str(e))
