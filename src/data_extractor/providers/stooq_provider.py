from __future__ import annotations
import logging

from data_extractor.core.base.base_provider import BaseProvider
from ..adapters.stooq_adapter import StooqAdapter

logger = logging.getLogger(__name__)


class StooqProvider(BaseProvider):
    """
    Provider de Stooq basado en BaseProvider:
      - Orquesta: adapter.get_symbols(...) -> normalizer_tipology(...)
    """
    def __init__(self, timeout: int = 30, max_workers: int = 8) -> None:
        adapter = StooqAdapter(timeout=timeout, max_workers=max_workers)
        super().__init__(source_name="stooq", adapter=adapter)
        logger.info(
            "StooqProvider init (timeout=%s, max_workers=%s)",
            timeout, max_workers
        )
