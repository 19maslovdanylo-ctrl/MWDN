class DomainException(Exception):
    """Represents base exception for all domain-level errors."""
    pass


class SupplyNotFoundException(DomainException):
    """Raised when a supply ID is not found."""

    def __init__(self, supply_id: str):
        self.supply_id = supply_id
        super().__init__(f"Supply '{supply_id}' not found")


class NoEligibleBiddersException(DomainException):
    """Raised when no bidders are eligible for an auction."""

    def __init__(self, supply_id: str, country: str):
        self.supply_id = supply_id
        self.country = country
        super().__init__(
            f"No eligible bidders for supply '{supply_id}' in country '{country}'"
        )


class NoBidsReceivedException(DomainException):
    """Raised when all eligible bidders skip bidding."""

    def __init__(self, supply_id: str, all_bids=None):
        self.supply_id = supply_id
        self.all_bids = all_bids or []
        super().__init__(
            f"No bids received for supply '{supply_id}' - all bidders skipped"
        )


class RateLimitExceededException(DomainException):
    """Raised when rate limit is exceeded for an IP address."""

    def __init__(self, ip_address: str, limit: int, window_seconds: int):
        self.ip_address = ip_address
        self.limit = limit
        self.window_seconds = window_seconds
        super().__init__(
            f"Rate limit exceeded for IP '{ip_address}': "
            f"max {limit} requests per {window_seconds} seconds"
        )
