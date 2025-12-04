from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.dependencies import get_db
from schemas.bidding import BidRequest, BidResponse, BidErrorResponse
from application.bidding_use_case import RunAuctionUseCase
from domain.bidding import (
    AuctionRequest,
    SimpleBidGenerator,
    AuctionService,
    SupplyNotFoundException,
    NoEligibleBiddersException,
    NoBidsReceivedException,
    RateLimitExceededException,
)
from infrastructure.repositories import BiddingRepository
from infrastructure.rate_limiter.redis_rate_limiter import get_rate_limiter
from core.logging import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/bid", tags=["bidding"])


async def get_auction_use_case(
    db: AsyncSession = Depends(get_db)
) -> RunAuctionUseCase:
    """Creates and configures the auction use case."""
    bidding_repo = BiddingRepository(db)
    rate_limiter = await get_rate_limiter()

    bid_generator = SimpleBidGenerator()
    auction_service = AuctionService(bid_generator)

    use_case = RunAuctionUseCase(
        bidding_repository=bidding_repo,
        rate_limiter=rate_limiter,
        auction_service=auction_service
    )

    return use_case


@router.post(
    "",
    response_model=BidResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "model": BidErrorResponse,
            "description": "No eligible bidders or no bids received"
        },
        404: {
            "model": BidErrorResponse,
            "description": "Supply not found"
        },
        429: {
            "model": BidErrorResponse,
            "description": "Rate limit exceeded"
        }
    }
)
async def run_auction(
    bid_request: BidRequest,
    use_case: RunAuctionUseCase = Depends(get_auction_use_case)
) -> BidResponse:
    """Runs an auction for a supply."""
    try:
        auction_request = AuctionRequest(
            supply_id=bid_request.supply_id,
            ip_address=bid_request.ip,
            country=bid_request.country,
            tmax=bid_request.tmax
        )

        result = await use_case.execute(auction_request)

        return BidResponse(
            winner=result.winner_bidder_id,
            price=result.winning_price
        )

    except RateLimitExceededException as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )

    except SupplyNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except (NoEligibleBiddersException, NoBidsReceivedException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Unexpected error in auction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
