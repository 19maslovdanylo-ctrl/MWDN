from abc import ABC, abstractmethod
from typing import Optional
from .entities import Supply, Bidder, Bid, AuctionResult


class IBiddingRepository(ABC):
    """Defines abstract repository interface for bidding operations."""

    @abstractmethod
    async def get_supply_by_id(self, supply_id: str) -> Optional[Supply]:
        """Retrieves a supply by its ID."""
        pass

    @abstractmethod
    async def get_or_create_supply(self, supply_id: str, name: Optional[str] = None) -> Supply:
        """Gets existing supply or creates a new one."""
        pass

    @abstractmethod
    async def get_eligible_bidders_for_supply(self, supply_id: str, country: str) -> list[Bidder]:
        """Gets all bidders eligible for a supply in a specific country."""
        pass

    @abstractmethod
    async def save_auction_result(
        self,
        supply_id: str,
        ip_address: str,
        country: str,
        result: AuctionResult,
        tmax: Optional[int] = None
    ) -> int:
        """Saves auction result and returns auction ID."""
        pass

    @abstractmethod
    async def save_bids(self, auction_id: int, bids: list[Bid]) -> None:
        """Saves all bids for an auction."""
        pass


class IRateLimiter(ABC):
    """Defines abstract rate limiter interface."""

    @abstractmethod
    async def check_rate_limit(
        self,
        key: str,
        max_requests: Optional[int] = None,
        window_seconds: Optional[int] = None
    ) -> bool:
        """Checks if request is within rate limit."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes the rate limiter (e.g., connect to Redis)."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Closes and cleanups rate limiter resources."""
        pass


class IBidGenerator(ABC):
    """Defines abstract bid generator interface for creating bids."""

    @abstractmethod
    async def generate_bid(
        self,
        bidder: Bidder,
        tmax: Optional[int] = None
    ) -> Bid:
        """Generates a bid for a bidder."""
        pass
