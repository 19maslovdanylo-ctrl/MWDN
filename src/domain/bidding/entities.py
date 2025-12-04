from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Supply:
    """Represents an advertising supply/inventory entity."""

    id: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.id:
            raise ValueError('Supply ID cannot be empty')


@dataclass
class Bidder:
    """Represents an advertising bidder/buyer entity."""

    id: str
    country: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.id:
            raise ValueError('Bidder ID cannot be empty')
        if not self.country or len(self.country) != 2:
            raise ValueError('Country must be a 2-letter ISO code')
        self.country = self.country.upper()

    def is_eligible_for_country(self, country: str) -> bool:
        """Checks if bidder is eligible for the given country."""
        return self.country.upper() == country.upper()


@dataclass
class Bid:
    """Represents a single bid in an auction."""

    bidder_id: str
    price: Optional[float] = None
    latency_ms: Optional[int] = None
    timed_out: bool = False

    def __post_init__(self):
        if not self.bidder_id:
            raise ValueError('Bidder ID cannot be empty')
        if self.price is not None and self.price < 0:
            raise ValueError('Bid price cannot be negative')
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError('Latency cannot be negative')

    @property
    def is_valid(self) -> bool:
        """Checks if bid is valid (has a price and didn't time out)."""
        return self.price is not None and not self.timed_out

    @property
    def is_no_bid(self) -> bool:
        """Checks if this represents a no-bid scenario."""
        return self.price is None and not self.timed_out


@dataclass
class AuctionRequest:
    """Contains all parameters for running an auction."""

    supply_id: str
    ip_address: str
    country: str
    tmax: Optional[int] = None

    def __post_init__(self):
        if not self.supply_id:
            raise ValueError('Supply ID cannot be empty')
        if not self.ip_address:
            raise ValueError('IP address cannot be empty')
        if not self.country or len(self.country) != 2:
            raise ValueError('Country must be a 2-letter ISO code')
        if self.tmax is not None and self.tmax <= 0:
            raise ValueError('tmax must be positive')
        self.country = self.country.upper()


@dataclass
class AuctionResult:
    """Represents the result of an auction execution."""

    winner_bidder_id: str
    winning_price: float
    all_bids: list[Bid]
    supply_id: str
    country: str

    def __post_init__(self):
        if not self.winner_bidder_id:
            raise ValueError('Winner bidder ID cannot be empty')
        if self.winning_price <= 0:
            raise ValueError('Winning price must be positive')
