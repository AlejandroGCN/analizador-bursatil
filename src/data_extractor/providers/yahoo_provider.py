# src/providers/yahoo_provider.py
from typing import Optional, Dict, List, Any, Union
import pandas as pd
import logging
from ..core.base import DataSource
from ..core.normalizer import normalizer_tipology   # ⬅️ orquestador (kind-agnostic)
from ..adapters.yahoo_adapter import YahooAdapter

logger = logging.getLogger(__name__)

class YahooProvider(DataSource):
    def __init__(self, timeout: int = 30, max_workers: int = 8):
        self.adapter = YahooAdapter(timeout=timeout, max_workers=max_workers)
        self.source_name = "yahoo"

    def get_data(
            self,
            symbol: str,
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str,
            *,
            kind: str = "ohlcv",
            align: Optional[str] = None,
            ffill: bool = False,
            bfill: bool = False,
            **options: Any,
    ):
        out = self.get_symbols(
            symbols_input=[symbol],
            start=start,
            end=end,
            interval=interval,
            kind=kind,
            align=align,
            ffill=ffill,
            bfill=bfill,
            **options,
        )
        return out.get(symbol)

    def get_symbols(
            self,
            symbols_input: Union[str, List[str]],
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str = "1d",
            *,
            kind: str = "ohlcv",
            align: Optional[str] = None,   # "intersect" | "union" | None
            ffill: bool = False,
            bfill: bool = False,
            **options: Any,                # ej.: window=20, ann_factor=252 para ciertas tipologías
    ) -> Dict[str, Any]:
        if isinstance(symbols_input, str):
            symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
        else:
            symbols = list(dict.fromkeys(symbols_input))

        raw_map = self.adapter.get_symbols(symbols, start, end, interval)
        return normalizer_tipology(
            raw_frames=raw_map,
            kind=kind,
            source_name=self.source_name,
            align=align,
            ffill=ffill,
            bfill=bfill,
            **options,
        )
