from typing import Any

from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models.bidding import (
    AuctionModel,
    BidModel,
    SupplyModel,
)


class StatsRepository:
    """
    Repository for statistics and analytics queries.
    Aggregates auction and bidding data for reporting.
    """

    def __init__(self, session: AsyncSession):
        """Initializes repository with database session."""
        self.session = session

    async def get_all_stats(self) -> dict[str, Any]:
        """Retrieves comprehensive statistics for all supplies."""
        supply_result = await self.session.execute(
            select(SupplyModel.id)
        )
        supply_ids = [row[0] for row in supply_result.all()]

        stats = {}
        for supply_id in supply_ids:
            stats[supply_id] = await self.get_supply_stats(supply_id)

        return stats

    async def get_supply_stats(self, supply_id: str) -> dict[str, Any]:
        """Retrieves statistics for specific supply."""
        auction_stats_query = select(
            func.count(AuctionModel.id).label('total_reqs'),
            AuctionModel.country,
            func.count(AuctionModel.country).label('country_count')
        ).where(
            AuctionModel.supply_id == supply_id
        ).group_by(
            AuctionModel.country
        )

        auction_result = await self.session.execute(auction_stats_query)
        auction_rows = auction_result.all()

        total_reqs = sum(row.country_count for row in auction_rows)
        reqs_per_country = {
            row.country: row.country_count for row in auction_rows}

        bidder_stats = await self.get_bidder_stats_for_supply(supply_id)

        return {
            "total_reqs": total_reqs,
            "reqs_per_country": reqs_per_country,
            "bidders": bidder_stats
        }

    async def get_bidder_stats_for_supply(
        self,
        supply_id: str
    ) -> dict[str, dict[str, Any]]:
        """Retrieves bidder statistics for specific supply."""
        query = select(
            BidModel.bidder_id,
            func.sum(
                case((AuctionModel.winner_bidder_id ==
                     BidModel.bidder_id, 1), else_=0)
            ).label('wins'),
            func.coalesce(
                func.sum(
                    case((AuctionModel.winner_bidder_id ==
                         BidModel.bidder_id, BidModel.price), else_=0)
                ),
                0
            ).label('total_revenue'),
            func.sum(
                case((and_(BidModel.price.is_(None),
                     BidModel.timed_out == 0), 1), else_=0)
            ).label('no_bids'),
            func.sum(
                case((BidModel.timed_out == 1, 1), else_=0)
            ).label('timeouts')
        ).join(
            AuctionModel, BidModel.auction_id == AuctionModel.id
        ).where(
            AuctionModel.supply_id == supply_id
        ).group_by(
            BidModel.bidder_id
        )

        result = await self.session.execute(query)
        rows = result.all()

        bidder_stats = {}
        for row in rows:
            stat_dict = {
                "wins": row.wins,
                "total_revenue": float(row.total_revenue),
                "no_bids": row.no_bids,
                "timeouts": row.timeouts
            }

            bidder_stats[row.bidder_id] = stat_dict

        return bidder_stats
