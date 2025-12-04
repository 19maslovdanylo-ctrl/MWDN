from pydantic import BaseModel, Field


class BidErrorResponse(BaseModel):
    """Error response model for bid endpoint."""

    error: str = Field(..., description="Error message")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "No eligible bidders found"
            }
        }
