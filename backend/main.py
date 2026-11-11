"""StackForge API entry point."""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routers import analyse, recommend, implement, upgrade

app = FastAPI(title="StackForge API", version="0.2.0")

# Only allow specifically trusted web applications, never the wildcard origin.
origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "https://stack-forge-xi.vercel.app,http://localhost:3000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    if request.method in ("POST", "PUT", "PATCH"):
        length = request.headers.get("content-length")
        if length:
            try:
                if int(length) > 40_000:
                    return JSONResponse(status_code=413, content={"detail": "Request too large."})
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length."})
    return await call_next(request)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

app.include_router(analyse.router)
app.include_router(recommend.router)
app.include_router(implement.router)
app.include_router(upgrade.router)
