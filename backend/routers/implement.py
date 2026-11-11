"""Authenticated implementation planning."""
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from backend.models.job import ImplementationPlanRequest
from backend.security import current_user_id, enforce_quota
from backend.services import gemini_service, supabase_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/implement", tags=["Implement"])

@router.post("/")
async def generate_implementation_plan(
    request: ImplementationPlanRequest,
    user_id: Annotated[str, Depends(current_user_id)],
):
    await enforce_quota(user_id, "implement")
    result = await gemini_service.generate_implementation_plan(
        request.project_title, request.project_description, request.tech_stack
    )
    if not isinstance(result, dict) or "error" in result:
        raise HTTPException(status_code=502, detail="Unable to generate an implementation plan. Please try again.")
    try:
        await supabase_service.save_project(user_id, {
            "title": request.project_title,
            "description": request.project_description,
            "tech_stack": request.tech_stack,
            "implementation_plan": result,
        })
    except Exception:
        logger.exception("Failed to persist implementation plan")
    return {"implementation_plan": result}
