"""Authenticated job analysis and history."""
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from backend.models.job import JobDescriptionRequest
from backend.security import current_user_id, enforce_quota
from backend.services import gemini_service, supabase_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyse", tags=["Analyse"])

@router.post("/")
async def analyse_job_description(
    request: JobDescriptionRequest,
    user_id: Annotated[str, Depends(current_user_id)],
):
    await enforce_quota(user_id, "analyse")
    result = await gemini_service.analyse_job_description(request.jd_text)
    if not isinstance(result, dict) or "error" in result:
        raise HTTPException(status_code=502, detail="Unable to generate analysis. Please try again.")
    try:
        await supabase_service.save_analysis(user_id, request.jd_text, result)
    except Exception:
        logger.exception("Failed to save analysis history")
        # The generated result is still useful. A database error is logged for repair.
    return {"analysis": result}

@router.get("/history")
async def get_analysis_history(user_id: Annotated[str, Depends(current_user_id)]):
    try:
        return {"history": await supabase_service.get_user_history(user_id)}
    except Exception:
        logger.exception("Failed to load history")
        raise HTTPException(status_code=503, detail="History is temporarily unavailable.")
