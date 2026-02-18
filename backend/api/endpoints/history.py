from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.services.history_service import history_service
from backend.services.logging import logger

router = APIRouter()

class SessionRequest(BaseModel):
    project_name: str
    actions: List[Dict[str, Any]]
    total_cost: int

@router.get("/api/history")
async def get_history():
    """Get all past sessions."""
    return history_service.get_history()

@router.post("/api/history")
async def save_session(session: SessionRequest):
    """Save a new session."""
    try:
        history_service.add_session(
            session.project_name,
            session.actions,
            session.total_cost
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to save session: {e}")
        raise HTTPException(500, str(e))
