"""
FastAPI Application Entry Point.
Configures CORS, middleware, REST routes, WebSocket streaming, and error handling.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import api_router
from app.api.ws import router as ws_router
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.errors import register_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    yield
    # Shutdown actions


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# 3. Structured Error Handlers
register_error_handlers(app)

# 4. Include REST and WebSocket Routers
app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for liveness verification."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
