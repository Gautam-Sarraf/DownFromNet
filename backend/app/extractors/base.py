from abc import ABC, abstractmethod
from app.schemas.media import MediaAnalysisResponse


class BaseExtractor(ABC):
    """Base interface for all media extractors."""
    name: str = "base"

    @abstractmethod
    async def can_handle(self, url: str) -> bool:
        """Return True if this extractor can process the given URL."""
        pass

    @abstractmethod
    async def extract(self, url: str) -> MediaAnalysisResponse:
        """Extract media metadata and downloadable formats from the URL."""
        pass
