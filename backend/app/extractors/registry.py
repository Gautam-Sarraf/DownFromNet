from typing import Optional
from app.extractors.base import BaseExtractor
from app.extractors.direct import DirectMediaExtractor
from app.extractors.ytdlp_extractor import YtDlpExtractor
from app.extractors.generic_html import GenericHtmlExtractor
from app.schemas.media import MediaAnalysisResponse
from app.core.errors import MediaNotFoundError


class ExtractorRegistry:
    def __init__(self):
        self.extractors: list[BaseExtractor] = [
            DirectMediaExtractor(),
            YtDlpExtractor(),
            GenericHtmlExtractor(),
        ]

    async def get_extractor_for_url(self, url: str) -> BaseExtractor:
        for ext in self.extractors:
            if await ext.can_handle(url):
                return ext
        # Fallback to generic
        return self.extractors[-1]

    async def extract(self, url: str) -> MediaAnalysisResponse:
        # First try matching specific extractor
        primary_extractor = await self.get_extractor_for_url(url)
        try:
            return await primary_extractor.extract(url)
        except Exception as primary_error:
            # If a specific extractor failed (e.g. ytdlp failed on an obscure web article),
            # try falling back to GenericHtmlExtractor if we haven't yet
            if not isinstance(primary_extractor, GenericHtmlExtractor):
                try:
                    generic = GenericHtmlExtractor()
                    return await generic.extract(url)
                except Exception:
                    pass
            # Re-raise the primary meaningful error
            raise primary_error


extractor_registry = ExtractorRegistry()
