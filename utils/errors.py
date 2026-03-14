class AppError(Exception):
    """Base application exception."""


class ValidationError(AppError):
    """Raised when inbound data fails validation."""


class ProcessingError(AppError):
    """Raised when a pipeline stage fails to process input."""


class AuthorizationError(AppError):
    """Raised when API auth requirements are not met."""
