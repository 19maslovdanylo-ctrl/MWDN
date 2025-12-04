import random
from typing import Optional

from core.settings import get_settings
from .entities import Bid, Bidder, AuctionResult
from .exceptions import NoBidsReceivedException
from .interfaces import IBidGenerator


class AuctionService:
    """Provides domain service for auction business logic."""

    def __init__(self, bid_generator: IBidGenerator):
        self.bid_generator = bid_generator

    async def run_auction(
            self,
            eligible_bidders: list[Bidder],
            supply_id: str,
            country: str,
            tmax: Optional[int] = None
    ) -> AuctionResult:
        """Runs an auction with eligible bidders and determines the winner."""
        if not eligible_bidders:
            raise NoBidsReceivedException(supply_id)

        all_bids = []
        for bidder in eligible_bidders:
            bid = await self.bid_generator.generate_bid(bidder, tmax)
            all_bids.append(bid)

        valid_bids = [bid for bid in all_bids if bid.is_valid]

        if not valid_bids:
            raise NoBidsReceivedException(supply_id, all_bids)

        winning_bid = max(valid_bids, key=lambda b: b.price)

        return AuctionResult(
            winner_bidder_id=winning_bid.bidder_id,
            winning_price=winning_bid.price,
            all_bids=all_bids,
            supply_id=supply_id,
            country=country
        )


class SimpleBidGenerator(IBidGenerator):
    """Implements simple bid generator with business rules."""

    def __init__(self):
        self.settings = get_settings()
        self.NO_BID_PROBABILITY = self.settings.no_bid_probability
        self.MIN_BID_PRICE = self.settings.min_bid_price
        self.MAX_BID_PRICE = self.settings.max_bid_price

    async def generate_bid(
            self,
            bidder: Bidder,
            tmax: Optional[int] = None
    ) -> Bid:
        """Generates a bid with business rules applied."""

        latency_ms = None

        if tmax:
            latency_ms = random.randint(self.settings.bidder_min_latency_ms, tmax + 50)

            if latency_ms > tmax:
                return Bid(
                    bidder_id=bidder.id,
                    price=None,
                    latency_ms=latency_ms,
                    timed_out=True
                )

        if random.random() < self.NO_BID_PROBABILITY:
            return Bid(
                bidder_id=bidder.id,
                price=None,
                latency_ms=latency_ms,
                timed_out=False
            )

        price = round(random.uniform(
            self.MIN_BID_PRICE, self.MAX_BID_PRICE
        ), 2)

        return Bid(
            bidder_id=bidder.id,
            price=price,
            latency_ms=latency_ms,
            timed_out=False
        )
