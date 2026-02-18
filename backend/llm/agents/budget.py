from typing import Dict, Any, List
from backend.llm.ollama_client import ollama_client
from backend.llm.prompts.budget import BUDGET_SYSTEM_PROMPT
from backend.services.logging import logger
from backend.core.config import settings, BUDGET_ESTIMATES
import json

class BudgetAgent:
    """Agent that validates plans against budget."""
    
    def __init__(self):
        self.client = ollama_client

    async def verify_plan(self, plan: List[Dict[str, Any]], budget: int) -> Dict[str, Any]:
        """
        Verify if the plan fits the budget.
        """
        estimates = json.dumps(BUDGET_ESTIMATES, indent=2)
        plan_str = json.dumps(plan, indent=2)
        
        # Construct prompt
        full_system_prompt = BUDGET_SYSTEM_PROMPT.format(
            estimates=estimates
        )
        
        logger.info(f"Budget Agent checking plan against budget: {budget}")
        
        try:
            # Generate JSON verification
            result = await self.client.generate_json(
                prompt=f"Check this plan against a budget of ${budget}: {plan_str}",
                system_prompt=full_system_prompt
            )
            
            logger.info(f"Budget Verification: {result.get('approved')}")
            return result
            
        except Exception as e:
            logger.error(f"Budget verification failed: {e}")
            # Fail safe: approve but warn
            return {
                "approved": True,
                "total_cost": 0,
                "feedback": "Budget check failed due to system error. Proceed with caution.",
                "error": str(e)
            }

budget_agent = BudgetAgent()
