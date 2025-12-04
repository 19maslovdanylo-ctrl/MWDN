from pydantic import BaseModel, Field


class BidderStats(BaseModel):
    """Statistics for a single bidder."""

    wins: int = Field(default=0, ge=0, description="Number of auction wins")
    total_revenue: float = Field(
        default=0.0, ge=0, description="Total revenue from wins")
    no_bids: int = Field(
        default=0, ge=0, description="Number of times bidder didn't bid")
    timeouts: int = Field(
        default=0, ge=0, description="Number of timeouts (optional requirement)")

    class Config:
        json_schema_extra = {
            "example": {
                "wins": 2,
                "total_revenue": 0.4,
                "no_bids": 3,
                "timeouts": 1
            }
        }
