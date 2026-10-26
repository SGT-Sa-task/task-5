"""Custom exceptions for Odoo XML-RPC integration."""


class OdooException(Exception):
    """Base exception for all Odoo related errors."""

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize OdooException with an optional details parameter."""
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        """Return formatted string representation of the exception."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class OdooConnectionError(OdooException):
    """Raised when connection to Odoo server fails or times out."""

    pass


class OdooAuthenticationError(OdooException):
    """Raised when authentication credentials or database name are invalid."""

    pass


class OdooOperationError(OdooException):
    """Raised when an XML-RPC operation (e.g., execute_kw) fails on Odoo."""

    pass
