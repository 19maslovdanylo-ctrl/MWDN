from .entities import AllSupplyStats


class StatsService:
    """Provides domain service for statistics business logic."""

    @staticmethod
    def transform_raw_stats(raw_stats: dict) -> AllSupplyStats:
        """Transforms raw statistics data into domain entities."""
        all_stats = AllSupplyStats()

        for supply_id, supply_data in raw_stats.items():
            supply_stats = all_stats.get_or_create_supply_stats(supply_id)

            supply_stats.total_reqs = supply_data.get("total_reqs", 0)
            supply_stats.reqs_per_country = supply_data.get(
                "reqs_per_country", {})

            bidders_data = supply_data.get("bidders", {})
            for bidder_id, bidder_data in bidders_data.items():
                bidder_stats = supply_stats.get_or_create_bidder_stats(
                    bidder_id)
                bidder_stats.wins = bidder_data.get("wins", 0)
                bidder_stats.total_revenue = bidder_data.get(
                    "total_revenue", 0.0)
                bidder_stats.no_bids = bidder_data.get("no_bids", 0)
                bidder_stats.timeouts = bidder_data.get("timeouts", 0)

        return all_stats

    @staticmethod
    def format_stats_for_response(stats: AllSupplyStats) -> dict:
        """Formats statistics for API response."""
        return stats.to_dict()
