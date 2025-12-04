from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class BidRequest(BaseModel):
    """Request model for POST /bid endpoint."""

    supply_id: str = Field(..., description="Supply identifier")
    ip: str = Field(..., description="Client IP address")
    country: str = Field(..., min_length=2, max_length=2,
                         description="Country code (2 letters)")
    tmax: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum time in milliseconds for bidder to respond (optional)"
    )

    @field_validator('ip')
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        """Validate that the IP address follows the IPv4 pattern."""
        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$'
        if not re.match(ipv4_pattern, v):
            raise ValueError(
                f"Invalid IP address format: '{v}'. "
                "Expected IPv4 format (e.g., 192.168.1.1)"
            )
        return v

    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Ensure country code is uppercase."""
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "supply_id": "supply1",
                "ip": "123.45.67.89",
                "country": "US",
                "tmax": 5000
            }
        }
