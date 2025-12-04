from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.dependencies import get_read_replica_db
from schemas.stats import SupplyStats
from application.stats_use_case import GetStatsUseCase
from domain.stats import StatsService
from infrastructure.repositories import StatsRepository
from core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/stat", tags=["statistics"])


async def get_stats_use_case(
    db: AsyncSession = Depends(get_read_replica_db)
) -> GetStatsUseCase:
    """Creates and configures the stats use case using read replica."""
    stats_repo = StatsRepository(db)
    stats_service = StatsService()

    use_case = GetStatsUseCase(
        stats_repository=stats_repo,
        stats_service=stats_service
    )

    return use_case


@router.get(
    "",
    response_model=dict[str, SupplyStats],
    status_code=status.HTTP_200_OK
)
async def get_statistics(
    use_case: GetStatsUseCase = Depends(get_stats_use_case)
) -> dict[str, SupplyStats]:
    """Retrieves auction statistics."""
    try:
        stats = await use_case.execute()
        return stats

    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
