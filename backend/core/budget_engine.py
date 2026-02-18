from typing import Dict, List, Any
from backend.core.config import settings, BUDGET_ESTIMATES
from backend.services.logging import logger

class BudgetEngine:
    """Core logic for cost estimation."""
    
    def __init__(self):
        self.estimates = BUDGET_ESTIMATES

    def calculate_item_cost(self, item_name: str, quality: str = "medium") -> int:
        """Get estimated cost for a single item."""
        # Normalize item name
        item_lower = item_name.lower()
        
        # Check direct mapping
        if item_lower in self.estimates:
            return self.estimates[item_lower].get(quality, self.estimates[item_lower]["medium"])
            
        # Check category mapping (simple heuristic)
        for category, costs in self.estimates.items():
            if category in item_lower:
                return costs.get(quality, costs["medium"])
                
        # Default fallback
        logger.warning(f"No cost estimate found for {item_name}, using default.")
        return 500 # Generic furniture cost

    def calculate_plan_cost(self, plan_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate total cost of a plan.
        Returns detailed breakdown.
        """
        total_cost = 0
        breakdown = []
        
        for step in plan_steps:
            action = step.get("action")
            target = step.get("target")
            
            cost = 0
            if action == "inpaint":
                # Assuming replacement involves buying new item
                cost = self.calculate_item_cost(target)
            elif action == "recolor":
                # Paint cost assumption (per room/wall)
                cost = 200 # Fixed paint cost estimate
                
            total_cost += cost
            breakdown.append({
                "action": action,
                "target": target,
                "estimated_cost": cost
            })
            
        return {
            "total_cost": total_cost,
            "breakdown": breakdown
        }

budget_engine = BudgetEngine()
