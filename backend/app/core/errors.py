from typing import Optional


class AppError(Exception):
    """Base application exception with user-friendly messages."""
    def __init__(self, message: str, status_code: int = 400, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class InvalidURLError(AppError):
    def __init__(self, message: str = "Invalid or malformed URL provided."):
        super().__init__(message=message, status_code=400)


class SSRFSecurityError(AppError):
    def __init__(self, message: str = "Access to local or private network addresses is restricted."):
        super().__init__(message=message, status_code=403)


class MediaNotFoundError(AppError):
    def __init__(self, message: str = "No downloadable media was found on the provided page."):
        super().__init__(message=message, status_code=404)


class MediaAccessDeniedError(AppError):
    def __init__(self, message: str = "This media could not be accessed. The website may require authentication or does not allow public downloads."):
        super().__init__(message=message, status_code=403)


class FileSizeLimitExceededError(AppError):
    def __init__(self, message: str = "This media exceeds the maximum allowed download size."):
        super().__init__(message=message, status_code=413)


class RateLimitExceededError(AppError):
    def __init__(self, message: str = "Too many requests. Please slow down and try again later."):
        super().__init__(message=message, status_code=429)


class ProcessingError(AppError):
    def __init__(self, message: str = "The media could not be processed or converted."):
        super().__init__(message=message, status_code=500)


class JobNotFoundError(AppError):
    def __init__(self, message: str = "The requested download task was not found or has expired."):
        super().__init__(message=message, status_code=404)
