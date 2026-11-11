"""Authenticated architecture upgrade analysis."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from backend.models.job import ProjectUpgradeRequest
from backend.security import current_user_id, enforce_quota
from backend.services import gemini_service

router = APIRouter(prefix="/upgrade", tags=["Upgrade"])

@router.post("/")
async def generate_upgrade_advice(
    request: ProjectUpgradeRequest,
    user_id: Annotated[str, Depends(current_user_id)],
):
    await enforce_quota(user_id, "upgrade")
    result = await gemini_service.generate_upgrade_advice(
        request.project_description, request.current_tech_stack
    )
    if not isinstance(result, dict) or "error" in result:
        raise HTTPException(status_code=502, detail="Unable to generate upgrade advice. Please try again.")
    return {"upgrade_advice": result}
