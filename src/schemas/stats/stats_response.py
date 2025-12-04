from pydantic import BaseModel, Field

from .supply_stats import SupplyStats


class StatsResponse(BaseModel):
    """Response model for GET /stat endpoint."""

    stats: dict[str, SupplyStats] = Field(
        default_factory=dict,
        description="Statistics grouped by supply ID"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "supply1": {
                    "total_reqs": 10,
                    "reqs_per_country": {"US": 5, "GB": 5},
                    "bidders": {
                        "bidder1": {
                            "wins": 2,
                            "total_revenue": 0.4,
                            "no_bids": 3,
                            "timeouts": 0
                        }
                    }
                }
            }
        }
