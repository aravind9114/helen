import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from backend.services.logging import logger
from backend.core.config import settings

HISTORY_FILE = settings.storage_dir / "history.json"

class HistoryService:
    """Manage session history."""
    
    def __init__(self):
        self._ensure_file()
        
    def _ensure_file(self):
        if not HISTORY_FILE.exists():
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)
                
    def get_history(self) -> List[Dict[str, Any]]:
        """Get all past sessions."""
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read history: {e}")
            return []
            
    def add_session(self, project_name: str, actions: List[Dict], total_cost: int):
        """Record a new session."""
        entry = {
            "id": int(datetime.now().timestamp()), # Simple ID
            "project_name": project_name,
            "actions": actions,
            "total_cost": total_cost,
            "timestamp": datetime.now().isoformat()
        }
        
        history = self.get_history()
        history.append(entry)
        
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=2)
            logger.info(f"Saved session to history: {project_name}")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

history_service = HistoryService()
