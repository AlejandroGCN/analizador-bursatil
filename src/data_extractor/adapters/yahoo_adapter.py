from __future__ import annotations
import logging
import pandas as pd
from data_extractor.core.base.base_adapter  import BaseAdapter
from data_extractor.core.errors import ExtractionError

logger = logging.getLogger(__name__)
class YahooAdapter(BaseAdapter):
    name = "yahoo"
    supports_intraday = True
    allowed_intervals = ["1d","1wk","1mo","1h","1m","5m","15m","30m","60m","90m"]

    def __init__(self, timeout: int = 30, max_workers: int = 8) -> None:
        super().__init__(timeout=timeout, max_workers=max_workers)
        import importlib.util as _u
        self._yf_available  = _u.find_spec("yfinance") is not None
        self._pdr_available = _u.find_spec("pandas_datareader") is not None
        if self._yf_available:
            import yfinance as yf  # type: ignore
            self.yf = yf
        if self._pdr_available:
            import pandas_datareader.data as pdr  # type: ignore
            self.pdr = pdr

    def _download_with_yfinance(self, symbol, start, end, interval) -> pd.DataFrame:
        t = self.yf.Ticker(symbol)
        df = t.history(start=start, end=end, interval=interval)
        if df is None or df.empty:
            raise ExtractionError(
                f"No se encontraron datos para '{symbol}' en Yahoo Finance",
                source="yfinance",
                symbol=symbol
            )
        # Asegura columnas mínimas para poder seleccionar después
        if "Adj Close" not in df.columns:
            df["Adj Close"] = df.get("Close")
        if "Volume" not in df.columns:
            df["Volume"] = 0.0
        return df[["Open","High","Low","Close","Adj Close","Volume"]]

    def _download_with_pdr(self, symbol, start, end) -> pd.DataFrame:
        df = self.pdr.get_data_yahoo(symbol, start=start, end=end)
        if df is None or df.empty:
            raise ExtractionError(
                f"No se encontraron datos para '{symbol}' en Yahoo Finance",
                source="pandas_datareader",
                symbol=symbol
            )
        if "Adj Close" not in df.columns:
            df["Adj Close"] = df.get("Close")
        if "Volume" not in df.columns:
            df["Volume"] = 0.0
        return df[["Open","High","Low","Close","Adj Close","Volume"]]

    def download_symbol(self, symbol, start, end, interval, **options) -> pd.DataFrame:
        if interval not in self.allowed_intervals:
            raise ExtractionError(f"Intervalo no soportado: {interval}", source=self.name)

        intradia = interval not in ("1d","1wk","1mo")

        if self._yf_available:
            df = self._download_with_yfinance(symbol, start, end, interval)
        else:
            if intradia:
                # pdr no sirve para intradía
                raise ExtractionError("Intradía requiere yfinance instalado", source=self.name)
            if not self._pdr_available:
                raise ExtractionError("Ni yfinance ni pandas_datareader disponibles", source=self.name)
            df = self._download_with_pdr(symbol, start, end)

        # Normalización y recorte coherentes para ambos backends
        df = self._finalize_ohlcv(df)
        df = self._clip_range(df, start, end)
        self._validate_ohlcv(df)
        sample = df.head(20)
        logger.info(
            "[%s] %d filas normalizadas, rango %s → %s\n%s",
            symbol, len(df), df.index.min(), df.index.max(),
            sample.to_string()
        )
        return df
