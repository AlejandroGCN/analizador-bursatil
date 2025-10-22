from __future__ import annotations
import logging

from data_extractor.core.base.base_provider import BaseProvider
from ..adapters.binance_adapter import BinanceAdapter

logger = logging.getLogger(__name__)

class BinanceProvider(BaseProvider):
    """
    Provider de Binance basado en BaseProvider.
    """
    def __init__(
            self,
            timeout: int = 30,
            max_workers: int = 8
    ) -> None:
        adapter = BinanceAdapter(timeout=timeout, max_workers=max_workers)
        super().__init__(source_name="binance", adapter=adapter)
        logger.info(
            "BinanceProvider init (timeout=%s, max_workers=%s)",
            timeout, max_workers
        )
