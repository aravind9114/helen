from fastapi import APIRouter, HTTPException
from backend.core.schemas import PlanRequest
from backend.llm.agents.planner import planner_agent
from backend.llm.agents.budget import budget_agent
from backend.services.web_suggest import WebSuggest
from backend.services.logging import logger

router = APIRouter()

@router.post("/api/plan")
async def create_plan(request: PlanRequest):
    """
    Generate an execution plan based on user request and detected items,
    and verify it against the budget.
    """
    logger.info(f"Planning request: {request.user_request} | Budget: {request.budget}")
    try:
        # Step 1: Generate Plan
        plan = await planner_agent.create_plan(
            user_request=request.user_request,
            detected_items=request.detected_items
        )
        
        # Step 1.5: Enhance Plan with Web Suggestions
        web_suggester = WebSuggest()
        if "steps" in plan and plan["steps"]:
            for step in plan["steps"]:
                action = step.get("action", "").lower()
                if action in ["inpaint", "replace", "suggest"]:
                    query = step.get("prompt") or step.get("target")
                    if query:
                        logger.info(f"Fetching suggestions for: {query}")
                        suggestions = web_suggester.search_suggestions(query, budget=request.budget, max_results=3)
                        step["suggestions"] = suggestions.get("results", [])

        # Step 2: Verify Budget (if plan generation succeeded)
        verification = {}
        if "steps" in plan and plan["steps"]:
            verification = await budget_agent.verify_plan(
                plan=plan["steps"],
                budget=request.budget
            )
        else:
             verification = {"approved": False, "feedback": "No steps generated to verify."}

        # Combine results
        return {
            "plan": plan,
            "verification": verification
        }
            
    except Exception as e:
        logger.error(f"Plan endpoint error: {e}")
        raise HTTPException(500, str(e))
