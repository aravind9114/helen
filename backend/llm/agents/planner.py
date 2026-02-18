from typing import List, Dict, Any, Optional
from backend.llm.ollama_client import ollama_client
from backend.llm.prompts.planner import PLANNER_SYSTEM_PROMPT
from backend.services.logging import logger

class PlannerAgent:
    """Agent that plans steps based on user request."""
    
    def __init__(self):
        self.client = ollama_client

    async def create_plan(self, user_request: str, detected_items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a plan for the user request.
        """
        # Format detections for prompt
        detections_str = "None"
        if detected_items:
            items = [item['label'] for item in detected_items]
            detections_str = ", ".join(items)
            
        # Construct prompt
        full_system_prompt = PLANNER_SYSTEM_PROMPT.format(
            user_request=user_request,
            detected_items=detections_str
        )
        
        logger.info(f"Planner Agent thinking on: {user_request}")
        
        try:
            # Generate JSON plan
            plan = await self.client.generate_json(
                prompt=f"Create a plan for: {user_request}",
                system_prompt=full_system_prompt
            )
            
            logger.info(f"Plan generated: {plan.get('summary')}")
            return plan
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {
                "error": str(e),
                "summary": "Failed to generate plan. Please try again.",
                "steps": []
            }

planner_agent = PlannerAgent()
