import pytest
from app.core.security import validate_url_security, sanitize_filename
from app.core.errors import SSRFSecurityError, InvalidURLError


def test_ssrf_blocks_localhost():
    with pytest.raises(SSRFSecurityError):
        validate_url_security("http://localhost:8000/api")

    with pytest.raises(SSRFSecurityError):
        validate_url_security("http://127.0.0.1:3000")

    with pytest.raises(SSRFSecurityError):
        validate_url_security("http://192.168.1.100/video.mp4")

    with pytest.raises(SSRFSecurityError):
        validate_url_security("http://10.0.0.1/stream.mp4")


def test_url_validation_accepts_public_urls():
    valid = validate_url_security("https://example.com/video.mp4")
    assert valid == "https://example.com/video.mp4"

    valid2 = validate_url_security("wikipedia.org/wiki/File:Sample.ogv")
    assert valid2.startswith("https://")


def test_sanitize_filename_traversal():
    dangerous = "../../../etc/passwd"
    safe = sanitize_filename(dangerous)
    assert ".." not in safe
    assert "/" not in safe
    assert safe.startswith("etc_passwd") or safe == "_etc_passwd"


def test_sanitize_filename_null_bytes_and_special():
    malicious = "test\x00file*name?<>.mp4"
    safe = sanitize_filename(malicious)
    assert "\x00" not in safe
    assert "*" not in safe
    assert "?" not in safe
