"""Trusted server-side Supabase access. Never expose the service-role key to the browser."""
import asyncio
import logging
import os
from datetime import datetime, timezone

from supabase import Client, create_client

logger = logging.getLogger(__name__)
LIMITS = {"analyse": 3, "implement": 3, "recommend": 10, "upgrade": 10}

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Client | None = create_client(url, key) if url and key else None
        if not self.client:
            logger.warning("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing; protected endpoints unavailable")

    @property
    def is_configured(self) -> bool:
        return self.client is not None

    async def verify_access_token(self, token: str) -> str | None:
        if not self.client:
            raise RuntimeError("Supabase is not configured")
        try:
            response = await asyncio.to_thread(self.client.auth.get_user, token)
            user = response.user
            return str(user.id) if user and user.id else None
        except Exception as exc:
            # Invalid or expired tokens are not internal service failures.
            code = getattr(exc, "status", None) or getattr(exc, "status_code", None)
            if code in (400, 401, 403):
                return None
            # Some GoTrue versions raise AuthApiError without a status attribute.
            if exc.__class__.__name__ in ("AuthApiError", "AuthInvalidJwtError"):
                return None
            raise

    async def consume_quota(self, user_id: str, feature: str) -> bool:
        if feature not in LIMITS:
            raise ValueError("Unsupported quota feature")
        if not self.client:
            raise RuntimeError("Supabase is not configured")
        now = datetime.now(timezone.utc).date()
        window = now.replace(day=1) if feature == "implement" else now
        args = {
            "p_user_id": user_id,
            "p_feature": feature,
            "p_limit": LIMITS[feature],
            "p_window_start": window.isoformat(),
        }
        response = await asyncio.to_thread(
            lambda: self.client.rpc("consume_api_quota", args).execute()
        )
        # Supabase/PostgREST returns a JSON boolean for this scalar RPC.
        if not isinstance(response.data, bool):
            raise RuntimeError("Unexpected quota RPC response")
        return response.data

    async def save_analysis(self, user_id: str, jd_text: str, result_json: dict):
        if not self.client:
            raise RuntimeError("Supabase is not configured")
        return await asyncio.to_thread(
            lambda: self.client.table("analyses").insert({
                "user_id": user_id, "jd_text": jd_text, "analysis_json": result_json
            }).execute()
        )

    async def get_user_history(self, user_id: str):
        if not self.client:
            raise RuntimeError("Supabase is not configured")
        result = await asyncio.to_thread(
            lambda: self.client.table("analyses")
            .select("id,jd_text,analysis_json,created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(25)
            .execute()
        )
        return result.data or []

    async def save_project(self, user_id: str, project_data: dict):
        if not self.client:
            raise RuntimeError("Supabase is not configured")
        return await asyncio.to_thread(
            lambda: self.client.table("saved_projects")
            .insert({**project_data, "user_id": user_id}).execute()
        )

supabase_service = SupabaseService()
