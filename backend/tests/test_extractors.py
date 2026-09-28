import pytest
from app.extractors.direct import DirectMediaExtractor
from app.extractors.registry import extractor_registry
from app.utils.mime import format_bytes, format_duration, get_media_type_from_ext


@pytest.mark.asyncio
async def test_direct_extractor_can_handle():
    direct = DirectMediaExtractor()
    assert await direct.can_handle("https://example.com/movie.mp4") is True
    assert await direct.can_handle("https://example.com/audio.mp3") is True
    assert await direct.can_handle("https://example.com/photo.jpg") is True
    assert await direct.can_handle("https://example.com/article.html") is False


def test_format_helpers():
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1048576 * 50) == "50.0 MB"
    assert format_duration(125) == "02:05"
    assert format_duration(3665) == "01:01:05"
    assert get_media_type_from_ext("mp4") == "video"
    assert get_media_type_from_ext("mp3") == "audio"
    assert get_media_type_from_ext("webp") == "image"
