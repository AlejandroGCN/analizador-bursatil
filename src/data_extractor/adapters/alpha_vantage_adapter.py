from __future__ import annotations
import os, logging, time
from typing import Optional, Any, Dict
import requests
import pandas as pd

from ..core.base_adapter import BaseAdapter
from ..core.errors import (
    SymbolNotFound,
    ExtractionError,
    RateLimitError,
    AuthError,
    BadRequestError,
    TemporaryNetworkError,
)

logger = logging.getLogger(__name__)


class AlphaVantageAdapter(BaseAdapter):
    """
    Adapter de Alpha Vantage (HTTPS REST).
    - Soporta daily y intradía (1m, 5m, 15m, 30m, 60m).
    - Devuelve DataFrame con OHLCV; incluye 'Adj Close' cuando procede.
    """
    name = "alpha_vantage"
    supports_intraday = True
    BASE_URL = "https://www.alphavantage.co/query"

    _INTRADAY_MAP = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "60m": "60min",
        "1h": "60min",
    }

    def __init__(
            self,
            api_key: Optional[str] = None,
            *,
            timeout: int = 30,
            max_workers: int = 5,
            respect_rate_limits: bool = True,
    ):
        super().__init__(timeout=timeout, max_workers=max_workers)
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        if not self.api_key:
            raise AuthError("Falta API key de Alpha Vantage", source=self.name)
        self.respect_rate_limits = respect_rate_limits

    def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
        except requests.Timeout:
            raise TemporaryNetworkError("Timeout en Alpha Vantage", source=self.name)
        except requests.RequestException as e:
            raise ExtractionError("Error de red Alpha Vantage", source=self.name, cause=e)

        if r.status_code == 401:
            raise AuthError("No autorizado en Alpha Vantage", source=self.name, status=401)
        if r.status_code >= 400:
            raise BadRequestError(
                f"HTTP {r.status_code} en Alpha Vantage",
                source=self.name, status=r.status_code, extra={"text": r.text}
            )

        data = r.json()
        # Mensajes típicos de AV: "Note" (rate-limit) y "Error Message" (bad request)
        if "Note" in data:
            if self.respect_rate_limits:
                # Pequeña espera “amable” para aliviar rate limit
                time.sleep(12)  # AV ~5 req/min → spacing
            raise RateLimitError(data.get("Note", "Rate limit"), source=self.name)
        if "Error Message" in data:
            raise BadRequestError(data["Error Message"], source=self.name)

        return data

    def _build_df_daily(self, data: Dict[str, Any]) -> pd.DataFrame:
        key = next((k for k in data.keys() if "Time Series" in k), None)
        if not key:
            raise ExtractionError("Payload inesperado (daily)", source=self.name, extra={"keys": list(data.keys())})

        ts = data[key]  # dict[date_str -> dict]
        if not ts:
            raise SymbolNotFound("Serie vacía (daily)", source=self.name)

        df = pd.DataFrame(ts).T
        # Columnas pueden ser "1. open", etc.
        rename_map = {
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. adjusted close": "Adj Close",
            "5. volume": "Volume",       # según endpoint; si es adjusted, '6. volume'
            "6. volume": "Volume",
        }
        df = df.rename(columns=rename_map)
        # Coerce numérico
        for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        # Índice datetime ascendente
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        # Si no hay Adj Close, usa Close como fallback (para homogeneidad)
        if "Adj Close" not in df.columns and "Close" in df.columns:
            df["Adj Close"] = df["Close"]
        return df[ [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns] ]

    def _build_df_intraday(self, data: Dict[str, Any]) -> pd.DataFrame:
        key = next((k for k in data.keys() if "Time Series" in k), None)
        if not key:
            raise ExtractionError("Payload inesperado (intraday)", source=self.name, extra={"keys": list(data.keys())})

        ts = data[key]
        if not ts:
            raise SymbolNotFound("Serie vacía (intraday)", source=self.name)

        df = pd.DataFrame(ts).T
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume",
        })
        for c in ["Open", "High", "Low", "Close", "Volume"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        # En intradía no hay adjusted close; crea fallback
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
        # ¿intradía o diario?
        if interval in self._INTRADAY_MAP:
            func = "TIME_SERIES_INTRADAY"
            av_interval = self._INTRADAY_MAP[interval]
            params = dict(function=func, symbol=symbol, interval=av_interval,
                          apikey=self.api_key, outputsize="full", datatype="json")
            data = self._request(params)
            df = self._build_df_intraday(data)
        else:
            # daily adjusted por defecto (mejor columnas)
            params = dict(function="TIME_SERIES_DAILY_ADJUSTED", symbol=symbol,
                          apikey=self.api_key, outputsize="full", datatype="json")
            data = self._request(params)
            df = self._build_df_daily(data)

        # Slice temporal si procede
        if start is not None:
            df = df[df.index >= pd.to_datetime(start)]
        if end is not None:
            df = df[df.index <= pd.to_datetime(end)]
        if df.empty:
            raise SymbolNotFound(f"Sin datos para {symbol} en rango", source=self.name, symbol=symbol)
        return df
