from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppError
from app.services.cleanup import cleanup_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background cleanup task
    await cleanup_service.start()
    yield
    # Shutdown: Stop cleanup task
    await cleanup_service.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade Universal Media Downloader backend with multi-source extraction, SSRF security, FFmpeg transcoding, and async batching.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_type": exc.__class__.__name__,
            "details": exc.details
        }
    )


# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)


# Root health redirect/check
@app.get("/health", tags=["Health"])
async def root_health():
    from app.api.routes.health import health_check
    return await health_check()


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/health"
    }
