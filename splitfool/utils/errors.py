"""Custom exception classes for Splitfool application."""


class SplitfoolError(Exception):
    """Base exception for all Splitfool errors."""

    def __init__(self, message: str, code: str) -> None:
        """Initialize error with message and code.

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
        """
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationError(SplitfoolError):
    """Raised when input validation fails."""

    pass


class UserNotFoundError(SplitfoolError):
    """Raised when user lookup fails."""

    pass


class BillNotFoundError(SplitfoolError):
    """Raised when bill lookup fails."""

    pass


class DuplicateUserError(SplitfoolError):
    """Raised when attempting to create a user with duplicate name."""

    pass


class UserHasBalancesError(SplitfoolError):
    """Raised when attempting to delete a user with outstanding balances."""

    pass
