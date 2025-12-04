from dataclasses import dataclass, field


@dataclass
class BidderStats:
    """Represents statistics for a single bidder within a supply."""

    wins: int = 0
    total_revenue: float = 0.0
    no_bids: int = 0
    timeouts: int = 0


@dataclass
class SupplyStats:
    """Represents statistics for a single supply."""

    total_reqs: int = 0
    reqs_per_country: dict[str, int] = field(default_factory=dict)
    bidders: dict[str, BidderStats] = field(default_factory=dict)

    def add_request(self, country: str) -> None:
        """Records a new auction request."""
        self.total_reqs += 1
        self.reqs_per_country[country] = self.reqs_per_country.get(
            country, 0) + 1

    def get_or_create_bidder_stats(self, bidder_id: str) -> BidderStats:
        """Gets existing bidder stats or creates new one."""
        if bidder_id not in self.bidders:
            self.bidders[bidder_id] = BidderStats()
        return self.bidders[bidder_id]

    def to_dict(self) -> dict:
        """Converts to dictionary for API response."""
        return {
            "total_reqs": self.total_reqs,
            "reqs_per_country": self.reqs_per_country,
            "bidders": {
                bidder_id: {
                    "wins": stats.wins,
                    "total_revenue": round(stats.total_revenue, 2),
                    "no_bids": stats.no_bids,
                    "timeouts": stats.timeouts,
                }
                for bidder_id, stats in self.bidders.items()
            }
        }


@dataclass
class AllSupplyStats:
    """Represents container for statistics of all supplies."""

    supplies: dict[str, SupplyStats] = field(default_factory=dict)

    def get_or_create_supply_stats(self, supply_id: str) -> SupplyStats:
        """Gets existing supply stats or creates new one."""
        if supply_id not in self.supplies:
            self.supplies[supply_id] = SupplyStats()
        return self.supplies[supply_id]

    def to_dict(self) -> dict[str, dict]:
        """Converts to dictionary for API response."""
        return {
            supply_id: stats.to_dict()
            for supply_id, stats in self.supplies.items()
        }
