from __future__ import annotations
import logging

from data_extractor.core.base.base_provider import BaseProvider
from ..adapters.alpha_vantage_adapter import AlphaVantageAdapter

logger = logging.getLogger(__name__)

class AlphaVantageProvider(BaseProvider):
    """
    Provider de Alpha Vantage basado en BaseProvider.
    """
    def __init__(
            self,
            api_key: str | None = None,
            timeout: int = 30,
            max_workers: int = 5,
            respect_rate_limits: bool = True
    ) -> None:
        adapter = AlphaVantageAdapter(
            api_key=api_key,
            timeout=timeout,
            max_workers=max_workers,
            respect_rate_limits=respect_rate_limits
        )
        super().__init__(source_name="alpha_vantage", adapter=adapter)
        logger.info(
            "AlphaVantageProvider init (api_key=%s, timeout=%s, max_workers=%s, respect_rate_limits=%s)",
            api_key, timeout, max_workers, respect_rate_limits
        )
