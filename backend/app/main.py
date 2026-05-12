from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.scheduler import start_scheduler, stop_scheduler
from app.routers import devices_router, heartbeats_router, stats_router, repos_router, websocket_router

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="CodePulse", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)

app.include_router(devices_router, prefix="/api")
app.include_router(heartbeats_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(repos_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.exception_handler(422)
async def custom_422_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": str(exc)}
    )

@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
