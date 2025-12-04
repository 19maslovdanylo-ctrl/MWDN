from typing import Optional
from pydantic import BaseModel, Field


class BidResponse(BaseModel):
    """Response model for POST /bid endpoint."""

    winner: str = Field(..., description="Winning bidder ID")
    price: float = Field(..., ge=0, description="Winning bid price")

    class Config:
        json_schema_extra = {
            "example": {
                "winner": "bidder2",
                "price": 0.83
            }
        }
