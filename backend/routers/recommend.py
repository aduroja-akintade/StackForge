"""Authenticated project recommendations."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from backend.models.job import ProjectRecommendationRequest
from backend.security import current_user_id, enforce_quota
from backend.services import gemini_service

router = APIRouter(prefix="/recommend", tags=["Recommend"])

@router.post("/")
async def recommend_projects(
    request: ProjectRecommendationRequest,
    user_id: Annotated[str, Depends(current_user_id)],
):
    await enforce_quota(user_id, "recommend")
    result = await gemini_service.recommend_projects(request.jd_text, request.current_skills)
    if not isinstance(result, dict) or "error" in result:
        raise HTTPException(status_code=502, detail="Unable to generate recommendations. Please try again.")
    return {"recommendations": result}
