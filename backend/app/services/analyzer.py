from app.core.security import validate_url_security
from app.extractors.registry import extractor_registry
from app.schemas.media import MediaAnalysisResponse


class AnalyzerService:
    async def analyze_url(self, url: str) -> MediaAnalysisResponse:
        # 1. Validate security / SSRF
        clean_url = validate_url_security(url)

        # 2. Extract using extractor registry
        result = await extractor_registry.extract(clean_url)
        return result


analyzer_service = AnalyzerService()
