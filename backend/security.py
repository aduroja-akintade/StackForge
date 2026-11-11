"""Authentication and atomic request quotas for protected API routes."""
import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)
_bearer = HTTPBearer(auto_error=False)

async def current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in to continue.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not supabase_service.is_configured:
        raise HTTPException(status_code=503, detail="Authentication is temporarily unavailable.")
    try:
        user_id = await supabase_service.verify_access_token(credentials.credentials)
    except Exception:
        logger.exception("Supabase token verification failed")
        raise HTTPException(status_code=503, detail="Authentication is temporarily unavailable.")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Your session has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id

async def enforce_quota(user_id: str, feature: str) -> None:
    """The database RPC increments usage atomically; errors fail closed."""
    try:
        accepted = await supabase_service.consume_quota(user_id, feature)
    except Exception:
        logger.exception("Quota backend unavailable for %s", feature)
        raise HTTPException(status_code=503, detail="Usage service is temporarily unavailable.")
    if not accepted:
        raise HTTPException(status_code=429, detail="Usage limit reached for this feature.")
