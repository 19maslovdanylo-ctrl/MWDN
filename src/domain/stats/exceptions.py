
class StatsException(Exception):
    """Represents base exception for stats-related errors."""
    pass


class StatsNotAvailableException(StatsException):
    """Raised when statistics are not available."""

    def __init__(self, message: str = "Statistics are not available"):
        super().__init__(message)
