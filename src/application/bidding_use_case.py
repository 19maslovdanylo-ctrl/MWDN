
from core.logging import get_logger
from core.settings import get_settings
from domain.bidding import (
    AuctionRequest,
    AuctionResult,
    AuctionService,
    IBiddingRepository,
    IRateLimiter,
    SupplyNotFoundException,
    NoEligibleBiddersException,
    NoBidsReceivedException,
    RateLimitExceededException,
)

logger = get_logger(__name__)


class RunAuctionUseCase:
    """Orchestrates the entire auction process."""

    def __init__(
            self,
            bidding_repository: IBiddingRepository,
            rate_limiter: IRateLimiter,
            auction_service: AuctionService
    ):
        self.bidding_repository = bidding_repository
        self.rate_limiter = rate_limiter
        self.auction_service = auction_service
        self.settings = get_settings()

    async def execute(self, request: AuctionRequest) -> AuctionResult:
        """Executes the auction use case."""
        logger.info(
            f"Starting auction for supply={request.supply_id}, "
            f"country={request.country}, ip={request.ip_address}"
        )
        is_allowed = await self.rate_limiter.check_rate_limit(
            key=request.ip_address,
            max_requests=self.settings.rate_limit_max_requests,
            window_seconds=self.settings.rate_limit_window_seconds
        )
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP: {request.ip_address}")
            raise RateLimitExceededException(
                ip_address=request.ip_address,
                limit=self.settings.rate_limit_max_requests,
                window_seconds=self.settings.rate_limit_window_seconds
            )
        supply = await self.bidding_repository.get_or_create_supply(
            supply_id=request.supply_id
        )
        if not supply:
            logger.error(f"Supply not found: {request.supply_id}")
            raise SupplyNotFoundException(request.supply_id)
        logger.debug(f"Supply validated: {supply.id}")
        eligible_bidders = await self.bidding_repository.get_eligible_bidders_for_supply(
            supply_id=request.supply_id,
            country=request.country
        )
        if not eligible_bidders:
            logger.warning(
                f"No eligible bidders for supply={request.supply_id}, "
                f"country={request.country}"
            )
            raise NoEligibleBiddersException(
                request.supply_id, request.country)

        logger.info(
            f"Found {len(eligible_bidders)} eligible bidders: "
            f"{[b.id for b in eligible_bidders]}"
        )

        try:
            result = await self.auction_service.run_auction(
                eligible_bidders=eligible_bidders,
                supply_id=request.supply_id,
                country=request.country,
                tmax=request.tmax
            )
            self._log_auction_details(request, result)
            auction_id = await self.bidding_repository.save_auction_result(
                supply_id=request.supply_id,
                ip_address=request.ip_address,
                country=request.country,
                result=result,
                tmax=request.tmax
            )

            await self.bidding_repository.save_bids(auction_id, result.all_bids)

            logger.info(
                f"Auction completed: winner={result.winner_bidder_id}, "
                f"price={result.winning_price}"
            )

            return result

        except NoBidsReceivedException as e:
            logger.warning(
                f"No valid bids received for supply={request.supply_id}, "
                f"country={request.country}, but saving for stats"
            )

            all_bids = e.all_bids

            self._log_failed_auction_details(request, all_bids)

            auction_id = await self.bidding_repository.save_auction_result(
                supply_id=request.supply_id,
                ip_address=request.ip_address,
                country=request.country,
                result=None,
                tmax=request.tmax
            )

            await self.bidding_repository.save_bids(auction_id, all_bids)

            await self.bidding_repository.session.commit()

            logger.info(
                f"Failed auction saved for stats: auction_id={auction_id}, "
                f"bids={len(all_bids)}"
            )

            raise

    def _log_auction_details(
        self,
        request: AuctionRequest,
        result: AuctionResult
    ) -> None:
        """Logs detailed auction information to terminal."""
        log_lines = [
            f"\n{'='*60}",
            f"Auction for {request.supply_id} (country={request.country}):",
        ]

        for bid in result.all_bids:
            if bid.timed_out:
                status = f"TIMEOUT (latency={bid.latency_ms}ms)"
            elif bid.is_no_bid:
                status = "no bid"
            else:
                latency_info = f", latency={bid.latency_ms}ms" if bid.latency_ms else ""
                status = f"price {bid.price:.2f}{latency_info}"

            log_lines.append(f"  {bid.bidder_id} - {status}")

        log_lines.append(
            f"Winner: {result.winner_bidder_id} ({result.winning_price:.2f})"
        )
        log_lines.append(f"{'='*60}\n")

        logger.info("\n".join(log_lines))

    def _log_failed_auction_details(
        self,
        request: AuctionRequest,
        all_bids: list
    ) -> None:
        """Logs detailed auction information for failed auctions (no valid bids)."""
        log_lines = [
            f"\n{'='*60}",
            f"FAILED Auction for {request.supply_id} (country={request.country}):",
        ]

        for bid in all_bids:
            if bid.timed_out:
                status = f"TIMEOUT (latency={bid.latency_ms}ms)"
            elif bid.is_no_bid:
                status = "no bid"
            else:
                latency_info = f", latency={bid.latency_ms}ms" if bid.latency_ms else ""
                status = f"price {bid.price:.2f}{latency_info}"

            log_lines.append(f"  {bid.bidder_id} - {status}")

        log_lines.append("Winner: None (no valid bids)")
        log_lines.append(f"{'='*60}\n")

        logger.info("\n".join(log_lines))
