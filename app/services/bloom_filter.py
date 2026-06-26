from pybloom_live import ScalableBloomFilter
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class BloomFilterService:

    def __init__(self):
        self._filter: Optional[ScalableBloomFilter] = None

    def initialize(self):
        self._filter = ScalableBloomFilter(
            initial_capacity=settings.bloom_filter_capacity,
            error_rate=settings.bloom_filter_error_rate,
            mode=ScalableBloomFilter.LARGE_SET_GROWTH,
        )
        logger.info(
            f"Bloom Filter initialized: capacity={settings.bloom_filter_capacity}, "
            f"error_rate={settings.bloom_filter_error_rate}"
        )

    async def add(self, short_code: str) -> bool:
        if not self._filter:
            self.initialize()
        was_present = short_code in self._filter
        self._filter.add(short_code)
        return was_present

    async def check(self, short_code: str) -> bool:
        if not self._filter:
            self.initialize()
        return short_code in self._filter

    @property
    def count(self) -> int:
        if not self._filter:
            return 0
        return len(self._filter)

    @property
    def capacity(self) -> int:
        return settings.bloom_filter_capacity


bloom_filter_service = BloomFilterService()
