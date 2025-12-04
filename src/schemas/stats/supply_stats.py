from pydantic import BaseModel, Field

from .bidder_stats import BidderStats


class SupplyStats(BaseModel):
    """Statistics for a single supply."""

    total_reqs: int = Field(
        default=0, ge=0, description='Total number of requests')
    reqs_per_country: dict[str, int] = Field(
        default_factory=dict,
        description='Request count per country code'
    )
    bidders: dict[str, BidderStats] = Field(
        default_factory=dict,
        description='Statistics per bidder'
    )

    class Config:
        json_schema_extra = {
            'example': {
                'total_reqs': 10,
                'reqs_per_country': {
                    'US': 5,
                    'GB': 5
                },
                'bidders': {
                    'bidder1': {
                        'wins': 2,
                        'total_revenue': 0.4,
                        'no_bids': 3,
                        'timeouts': 0
                    },
                    'bidder2': {
                        'wins': 3,
                        'total_revenue': 0.7,
                        'no_bids': 1,
                        'timeouts': 1
                    }
                }
            }
        }
