from typing import Dict
from core.logging import get_logger
from domain.stats import IStatsRepository, StatsService


logger = get_logger(__name__)


class GetStatsUseCase:
    """Orchestrates retrieval of auction statistics."""

    def __init__(
            self,
            stats_repository: IStatsRepository,
            stats_service: StatsService
    ):
        self.stats_repository = stats_repository
        self.stats_service = stats_service

    async def execute(self) -> Dict[str, dict]:
        """Executes the get statistics use case."""
        logger.info("Fetching all statistics")
        raw_stats = await self.stats_repository.get_all_stats()
        logger.debug(f"Retrieved stats for {len(raw_stats)} supplies")
        stats_entities = self.stats_service.transform_raw_stats(raw_stats)
        formatted_stats = self.stats_service.format_stats_for_response(
            stats_entities)
        logger.info(
            f"Statistics retrieved successfully for {len(formatted_stats)} supplies")
        return formatted_stats
