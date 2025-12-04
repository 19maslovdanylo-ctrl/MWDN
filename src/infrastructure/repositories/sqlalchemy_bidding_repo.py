from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infrastructure.db.models.bidding import (
    AuctionModel,
    BidModel,
    BidderModel,
    SupplyModel,
    supply_bidder_association
)


class BiddingRepository:
    """
    Repository for managing bidding-related database operations.
    Handles supplies, bidders, auctions, and bids.
    """

    def __init__(self, session: AsyncSession):
        """Initializes repository with database session."""
        self.session = session

    async def get_supply_by_id(self, supply_id: str) -> Optional[SupplyModel]:
        """Retrieves supply by ID with preloaded bidders."""
        result = await self.session.execute(
            select(SupplyModel)
            .options(selectinload(SupplyModel.bidders))
            .where(SupplyModel.id == supply_id)
        )
        return result.scalar_one_or_none()

    async def create_supply(
        self,
        supply_id: str,
        name: Optional[str] = None
    ) -> SupplyModel:
        """Creates new supply record."""
        supply = SupplyModel(id=supply_id, name=name)
        self.session.add(supply)
        await self.session.flush()
        return supply

    async def get_or_create_supply(
        self,
        supply_id: str,
        name: Optional[str] = None
    ) -> SupplyModel:
        """Gets existing supply or creates new one if not found."""
        supply = await self.get_supply_by_id(supply_id)
        if not supply:
            supply = await self.create_supply(supply_id, name)
        return supply

    async def get_bidder_by_id(self, bidder_id: str) -> Optional[BidderModel]:
        """Retrieves bidder by ID."""
        result = await self.session.execute(
            select(BidderModel).where(BidderModel.id == bidder_id)
        )
        return result.scalar_one_or_none()

    async def create_bidder(
        self,
        bidder_id: str,
        country: str,
        name: Optional[str] = None
    ) -> BidderModel:
        """Creates new bidder record."""
        bidder = BidderModel(id=bidder_id, country=country, name=name)
        self.session.add(bidder)
        await self.session.flush()
        return bidder

    async def get_eligible_bidders_for_supply(
        self,
        supply_id: str,
        country: str
    ) -> list[BidderModel]:
        """Retrieves bidders eligible for supply filtered by country."""
        result = await self.session.execute(
            select(BidderModel)
            .join(supply_bidder_association)
            .where(
                and_(
                    supply_bidder_association.c.supply_id == supply_id,
                    BidderModel.country == country
                )
            )
        )
        return list(result.scalars().all())

    async def create_auction(
        self,
        supply_id: str,
        ip_address: str,
        country: str,
        tmax: Optional[int] = None,
        winner_bidder_id: Optional[str] = None,
        winning_price: Optional[float] = None
    ) -> AuctionModel:
        """Creates new auction record."""
        auction = AuctionModel(
            supply_id=supply_id,
            ip_address=ip_address,
            country=country,
            tmax=tmax,
            winner_bidder_id=winner_bidder_id,
            winning_price=winning_price
        )
        self.session.add(auction)
        await self.session.flush()
        return auction

    async def create_bid(
        self,
        auction_id: int,
        bidder_id: str,
        price: Optional[float] = None,
        latency_ms: Optional[int] = None,
        timed_out: int = 0
    ) -> BidModel:
        """Creates new bid record."""
        bid = BidModel(
            auction_id=auction_id,
            bidder_id=bidder_id,
            price=price,
            latency_ms=latency_ms,
            timed_out=timed_out
        )
        self.session.add(bid)
        await self.session.flush()
        return bid

    async def save_auction_result(
        self,
        supply_id: str,
        ip_address: str,
        country: str,
        result,
        tmax: Optional[int] = None
    ) -> int:
        winner_bidder_id = None
        winning_price = None

        if result is not None:
            winner_bidder_id = getattr(result, "winner_bidder_id", None)
            winning_price = getattr(result, "winning_price", None)

        auction = await self.create_auction(
            supply_id=supply_id,
            ip_address=ip_address,
            country=country,
            tmax=tmax,
            winner_bidder_id=winner_bidder_id,
            winning_price=winning_price
        )
        return auction.id

    async def save_bids(self, auction_id: int, bids: list) -> None:
        for bid in bids:
            bidder_id = getattr(
                bid, "bidder_id", None) or getattr(bid, "id", None)
            price = getattr(bid, "price", None)
            latency_ms = getattr(bid, "latency_ms", None)
            timed_out = getattr(bid, "timed_out", 0)

            await self.create_bid(
                auction_id=auction_id,
                bidder_id=bidder_id,
                price=price,
                latency_ms=latency_ms,
                timed_out=int(bool(timed_out)),
            )
