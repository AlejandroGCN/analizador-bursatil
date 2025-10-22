from __future__ import annotations
import logging
from typing import Optional, Any, Dict, List
import requests
import pandas as pd

from ..core.base_adapter import BaseAdapter
from ..core.errors import (
    SymbolNotFound,
    ExtractionError,
    BadRequestError,
    TemporaryNetworkError,
)

logger = logging.getLogger(__name__)


class BinanceAdapter(BaseAdapter):
    """
    Adapter de Binance (REST klines).
    - Soporta spot klines públicos (no requiere API key).
    - Devuelve OHLCV; 'Adj Close' = 'Close' por homogeneidad.
    """
    name = "binance"
    supports_intraday = True
    BASE_URL = "https://api.binance.com"

    # Mapeo directo de intervalos típicos
    _INTERVALS = {
        "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h", "6h": "6h", "8h": "8h", "12h": "12h",
        "1d": "1d", "3d": "3d", "1w": "1w", "1M": "1M",
    }

    @staticmethod
    def _ts_ms(ts: Optional[pd.Timestamp]) -> Optional[int]:
        if ts is None:
            return None
        return int(pd.Timestamp(ts).value // 10**6)

    def _request_klines(
            self, symbol: str, interval: str,
            start: Optional[pd.Timestamp], end: Optional[pd.Timestamp],
            limit: int = 1000,
    ) -> List[list]:
        params: Dict[str, Any] = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        if start is not None:
            params["startTime"] = self._ts_ms(start)
        if end is not None:
            params["endTime"] = self._ts_ms(end)

        try:
            r = requests.get(f"{self.BASE_URL}/api/v3/klines", params=params, timeout=self.timeout)
        except requests.Timeout:
            raise TemporaryNetworkError("Timeout en Binance", source=self.name)
        except requests.RequestException as e:
            raise ExtractionError("Error de red en Binance", source=self.name, cause=e)

        if r.status_code == 400:
            raise BadRequestError(f"Bad request Binance: {r.text}", source=self.name, status=400)
        if r.status_code >= 400:
            raise ExtractionError(f"HTTP {r.status_code} en Binance", source=self.name, status=r.status_code, extra={"text": r.text})

        data = r.json()
        if not isinstance(data, list):
            # Binance suele devolver {"code":-1121,"msg":"Invalid symbol."}
            msg = getattr(data, "get", lambda *_: None)("msg") if hasattr(data, "get") else str(data)
            if "Invalid symbol" in str(msg):
                raise SymbolNotFound(f"Símbolo no válido en Binance: {symbol}", source=self.name, symbol=symbol)
            raise ExtractionError("Respuesta inesperada Binance", source=self.name, extra={"data": data})
        return data

    def _build_df(self, klines: List[list]) -> pd.DataFrame:
        if not klines:
            raise SymbolNotFound("Serie vacía Binance", source=self.name)
        cols = [
            "Open time", "Open", "High", "Low", "Close", "Volume",
            "Close time", "Quote asset volume", "Number of trades",
            "Taker buy base volume", "Taker buy quote volume", "Ignore"
        ]
        df = pd.DataFrame(klines, columns=cols)
        # Convertir a tipos correctos
        num_cols = ["Open", "High", "Low", "Close", "Volume"]
        for c in num_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        # Índice de tiempo
        df["Open time"] = pd.to_datetime(df["Open time"], unit="ms", utc=True).dt.tz_convert(None)
        df = df.set_index("Open time").sort_index()
        # Adj Close como Close por homogeneidad con normalizer
        df["Adj Close"] = df["Close"]
        return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]

    def download_symbol(
            self,
            symbol: str,
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str,
            **options: Any,
    ) -> pd.DataFrame:
        if interval not in self._INTERVALS:
            # Fallback razonable
            logger.warning("Intervalo %s no soportado en Binance; se fuerza 1h", interval)
            interval = "1h"
        # Binance no devuelve más de 1000 velas por request; para rangos muy largos
        # podrías paginar (no lo hacemos aquí para mantener simple y dejarlo al caller).
        kl = self._request_klines(symbol, self._INTERVALS[interval], start, end, limit=1000)
        df = self._build_df(kl)
        # slice adicional por seguridad (si start/end vienen sin milisegundos exactos)
        if start is not None:
            df = df[df.index >= pd.to_datetime(start)]
        if end is not None:
            df = df[df.index <= pd.to_datetime(end)]
        if df.empty:
            raise SymbolNotFound(f"Sin datos para {symbol} en rango", source=self.name, symbol=symbol)
        return df
