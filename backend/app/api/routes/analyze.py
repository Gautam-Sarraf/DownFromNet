from fastapi import APIRouter, Request, HTTPException
from app.core.rate_limit import rate_limiter
from app.schemas.media import AnalyzeRequest, MediaAnalysisResponse
from app.services.analyzer import analyzer_service

router = APIRouter(tags=["Analyze"])


@router.post("/analyze", response_model=MediaAnalysisResponse)
async def analyze_url(request: Request, body: AnalyzeRequest):
    # Enforce rate limit
    rate_limiter.check_limit(request, endpoint_type="analyze")

    if not body.url or not body.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    result = await analyzer_service.analyze_url(body.url.strip())
    return result
