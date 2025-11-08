from __future__ import annotations
from typing import Any, Dict, List, Optional
import logging
import requests
import pandas as pd
from data_extractor.core.base.base_adapter import BaseAdapter
from data_extractor.core.errors import ExtractionError, SymbolNotFound
logger = logging.getLogger(__name__)

_BINANCE_URL = "https://api.binance.com/api/v3/klines"

class BinanceAdapter(BaseAdapter):
    name = "binance"
    supports_intraday = True
    allowed_intervals = ["1m","3m","5m","15m","30m","1h","2h","4h","6h","8h","12h","1d","3d","1w","1M"]

    def __init__(self, timeout: int = 30, max_workers: int = 8, session: Optional[requests.Session] = None) -> None:
        super().__init__(timeout=timeout, max_workers=max_workers)
        self._session = session or requests.Session()

    def download_symbol(
            self,
            symbol: str,
            start: Optional[Any],
            end: Optional[Any],
            interval: str,
            **options: Any
    ) -> pd.DataFrame:
        if interval not in self.allowed_intervals:
            raise ExtractionError(f"Intervalo no soportado: {interval}", source=self.name)

        manual_limit = options.get("limit")
        limit = int(manual_limit) if manual_limit is not None else 1000
        # Binance acepta máximo 1000 klines por request
        limit = max(1, min(limit, 1000))

        end_ms = int(pd.to_datetime(end).timestamp() * 1000) if end is not None else None
        # Paginar únicamente cuando el usuario pide un rango histórico amplio
        should_paginate = manual_limit is None and start is not None

        next_start_ms: Optional[int] = (
            int(pd.to_datetime(start).timestamp() * 1000) if start is not None else None
        )

        frames: List[pd.DataFrame] = []

        while True:
            params: Dict[str, Any] = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
            }

            if next_start_ms is not None:
                params["startTime"] = next_start_ms
            if end_ms is not None:
                params["endTime"] = end_ms

            resp = self._session.get(_BINANCE_URL, params=params, timeout=self.timeout)
            if resp.status_code >= 400:
                try:
                    payload = resp.json()
                except (ValueError, TypeError, requests.exceptions.JSONDecodeError):
                    payload = {}
                if isinstance(payload, dict) and payload.get("code") == -1121:
                    raise SymbolNotFound(f"Símbolo inválido: {symbol}", source=self.name)
                raise ExtractionError(f"HTTP {resp.status_code}: {getattr(resp, 'text', '')}", source=self.name)

            raw = resp.json()
            if not raw:
                break

            cols = ["openTime","open","high","low","close","volume","closeTime"]
            rows = [[it[0], it[1], it[2], it[3], it[4], it[5], it[6]] for it in raw]
            chunk = pd.DataFrame(rows, columns=cols)
            chunk["openTime"] = pd.to_datetime(chunk["openTime"], unit="ms")
            chunk.set_index("openTime", inplace=True)
            chunk.rename(columns={
                "open": "Open", "high": "High", "low": "Low",
                "close": "Close", "volume": "Volume"
            }, inplace=True)
            numeric_cols = ["Open","High","Low","Close","Volume"]
            chunk[numeric_cols] = chunk[numeric_cols].apply(pd.to_numeric, errors="coerce")
            frames.append(chunk)

            if not should_paginate:
                break

            if len(raw) < limit:
                break

            last_open_ms = raw[-1][0]
            if end_ms is not None and last_open_ms >= end_ms:
                break

            new_start_ms = last_open_ms + 1
            if next_start_ms is not None and new_start_ms <= next_start_ms:
                break
            next_start_ms = new_start_ms

        if not frames:
            raise ExtractionError("No se encontraron datos para el rango solicitado", source=self.name)

        df = pd.concat(frames)

        df = self._finalize_ohlcv(df)
        df = self._clip_range(df, start, end)

        sample = df.head(20)
        logger.info(
            "[%s] %d filas normalizadas, rango %s → %s\n%s",
            symbol, len(df), df.index.min(), df.index.max(),
            sample.to_string()
        )
        return df
