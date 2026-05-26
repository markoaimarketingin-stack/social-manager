from fastapi import APIRouter, Depends, HTTPException
from social_manager.routers.users import get_current_user
from social_manager.state import SocialManagerState
from social_manager.graph import build_social_strategy
from typing import Dict, Any

router = APIRouter(prefix="/api/strategy", tags=["AI Strategy"])

@router.post("/generate")
async def generate_strategy(
    input_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """
    Generate a full AI social strategy.
    input_data should contain brand_profile, target_persona, etc.
    """
    try:
        # Create initial state from user input
        initial_state = SocialManagerState(
            brand_profile=input_data.get("brand_profile", {}),
            target_persona=input_data.get("target_persona", {}),
            active_platforms=input_data.get("active_platforms", ["instagram", "x"]),
            structured_context=input_data.get("context", {})
        )
        
        # Run the multi-agent graph
        final_state = build_social_strategy(initial_state)
        
        return {
            "status": "success",
            "strategy": {
                "pillars": final_state.content_pillars,
                "calendar": final_state.monthly_calendar,
                "suggestions": final_state.suggestions_list,
                "engagement_plan": final_state.engagement_plan,
                "influencer_strategy": final_state.influencer_strategy
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")

@router.get("/current")
async def get_current_strategy(current_user = Depends(get_current_user)):
    """Fetch the latest generated strategy for this user (mocked for now)."""
    return {"status": "no_strategy_active"}
