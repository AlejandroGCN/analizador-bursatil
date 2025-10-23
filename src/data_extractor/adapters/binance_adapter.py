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

        params: Dict[str, Any] = {"symbol": symbol, "interval": interval}
        # respeta limit si viene en options (p. ej. para tests)
        if "limit" in options and options["limit"] is not None:
            params["limit"] = int(options["limit"])

        if start is not None:
            params["startTime"] = int(pd.to_datetime(start).timestamp() * 1000)
        if end is not None:
            params["endTime"] = int(pd.to_datetime(end).timestamp() * 1000)

        resp = self._session.get(_BINANCE_URL, params=params, timeout=self.timeout)
        # errores típicos de Binance: 400 con {"code": -1121, ...}
        if resp.status_code >= 400:
            try:
                payload = resp.json()
            except Exception:
                payload = {}
            if isinstance(payload, dict) and payload.get("code") == -1121:
                raise SymbolNotFound(f"Símbolo inválido: {symbol}", source=self.name)
            raise ExtractionError(f"HTTP {resp.status_code}: {getattr(resp, 'text', '')}", source=self.name)

        raw = resp.json()
        # cada kline: [openTime, open, high, low, close, volume, closeTime, ...]
        cols = ["openTime","open","high","low","close","volume","closeTime"]
        rows: List[List[Any]] = []
        for it in raw:
            rows.append([it[0], it[1], it[2], it[3], it[4], it[5], it[6]])

        df = pd.DataFrame(rows, columns=cols)
        df["openTime"] = pd.to_datetime(df["openTime"], unit="ms")
        df.set_index("openTime", inplace=True)
        df.rename(columns={
            "open": "Open", "high": "High", "low": "Low",
            "close": "Close", "volume": "Volume"
        }, inplace=True)

        # tipajes numéricos
        for c in ["Open","High","Low","Close","Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = self._finalize_ohlcv(df)
        df = self._clip_range(df, start, end)

        sample = df.head(20)
        logger.info(
            "[%s] %d filas normalizadas, rango %s → %s\n%s",
            symbol, len(df), df.index.min(), df.index.max(),
            sample.to_string()
        )
        return df
