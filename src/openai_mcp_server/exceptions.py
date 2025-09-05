"""Custom exceptions for the OpenAI MCP Server."""

from typing import Any


class OpenAIMCPError(Exception):
    """Base exception for OpenAI MCP Server."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class APIError(OpenAIMCPError):
    """Exception for OpenAI API related errors."""
    
    def __init__(self, message: str, status_code: int | None = None, **kwargs):
        super().__init__(message, kwargs)
        self.status_code = status_code


class CacheError(OpenAIMCPError):
    """Exception for cache-related errors."""
    pass


class ContentValidationError(OpenAIMCPError):
    """Exception for content validation errors."""
    
    def __init__(self, message: str, content_type: str, **kwargs):
        super().__init__(message, kwargs)
        self.content_type = content_type


class ConfigurationError(OpenAIMCPError):
    """Exception for configuration-related errors."""
    pass


class ProcessingError(OpenAIMCPError):
    """Exception for processing-related errors."""
    
    def __init__(self, message: str, operation: str, **kwargs):
        super().__init__(message, kwargs)
        self.operation = operation


class RateLimitError(APIError):
    """Exception for rate limiting errors."""
    
    def __init__(self, message: str, retry_after: int | None = None, **kwargs):
        super().__init__(message, 429, **kwargs)
        self.retry_after = retry_after