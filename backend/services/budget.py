"""
Budget estimation service using rule-based approach.
"""
from backend.core.config import settings, BUDGET_ESTIMATES


def estimate_cost(style: str) -> int:
    """
    Estimate the cost based on the selected design style.
    
    Args:
        style: Design style (Minimalist, Modern, Vintage, Professional)
        
    Returns:
        Estimated cost in currency units
    """
    return BUDGET_ESTIMATES.get(style, 200000)


def check_budget_status(estimated_cost: int, budget: int) -> str:
    """
    Check if the estimated cost is within budget.
    
    Args:
        estimated_cost: Estimated cost of the design
        budget: User's budget
        
    Returns:
        "within_budget" or "over_budget"
    """
    return "within_budget" if budget >= estimated_cost else "over_budget"
