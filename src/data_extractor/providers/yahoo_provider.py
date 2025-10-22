# providers/yahoo_provider.py
from __future__ import annotations
import logging

from data_extractor.core.base.base_provider import BaseProvider
from ..adapters.yahoo_adapter import YahooAdapter

logger = logging.getLogger(__name__)


class YahooProvider(BaseProvider):
    """
    Provider de Yahoo Finance basado en BaseProvider.
    """
    def __init__(self, timeout: int = 30, max_workers: int = 8) -> None:
        adapter = YahooAdapter(timeout=timeout, max_workers=max_workers)
        super().__init__(source_name="yahoo", adapter=adapter)
        logger.info("YahooProvider init (timeout=%s, max_workers=%s)", timeout, max_workers)
