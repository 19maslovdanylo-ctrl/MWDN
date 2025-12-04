from abc import ABC, abstractmethod
from typing import Dict, Any


class IStatsRepository(ABC):
    """Defines abstract repository interface for statistics operations."""

    @abstractmethod
    async def get_all_stats(self) -> dict[str, Any]:
        """Retrieves comprehensive statistics for all supplies."""
        pass

    @abstractmethod
    async def get_supply_stats(self, supply_id: str) -> dict[str, Any]:
        """Retrieves statistics for a specific supply."""
        pass
