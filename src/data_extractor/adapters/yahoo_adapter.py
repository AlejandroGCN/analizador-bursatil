# adapters/yahoo_adapter.py
import warnings
import logging
import pandas as pd
from importlib import util as importlib_util
from typing import Optional, Any

from data_extractor.core.base.base_adapter import BaseAdapter
from ..core.errors import SymbolNotFound, ExtractionError

logger = logging.getLogger(__name__)


class YahooAdapter(BaseAdapter):
    """
    Adapter para obtener datos desde Yahoo Finance (yfinance / pandas_datareader).
    Hereda la lógica de paralelización y normalización de símbolos de BaseAdapter.
    """
    name = "yahoo"
    supports_intraday = True

    def __init__(self, timeout: int = 30, max_workers: int = 8):
        super().__init__(timeout=timeout, max_workers=max_workers)

        self._yf = importlib_util.find_spec("yfinance") is not None
        self._pdr = importlib_util.find_spec("pandas_datareader") is not None
        if self._yf:
            import yfinance as yf  # type: ignore
            try:
                yf.shared._DFS_CACHE.enable()
            except Exception:
                pass
            self.yf = yf
        if self._pdr:
            import pandas_datareader.data as pdr  # type: ignore
            self.pdr = pdr

        if not (self._yf or self._pdr):
            raise ImportError("Necesitas 'yfinance' o 'pandas_datareader' para usar YahooAdapter.")

    def download_symbol(
            self,
            symbol: str,
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str,
            **options: Any,
    ) -> pd.DataFrame:
        last: Optional[Exception] = None

        if self._yf:
            try:
                df = self.yf.download(
                    symbol, start=start, end=end, interval=interval,
                    progress=False, threads=False
                )
                if df is None or df.empty:
                    raise SymbolNotFound(
                        message=f"Símbolo no encontrado: {symbol}",
                        source="yahoo/yfinance",
                        symbol=symbol,
                    )
                return df
            except Exception as e:
                last = e
                logger.exception("Fallo en yfinance para %s", symbol)

        if self._pdr:
            try:
                if interval != "1d":
                    warnings.warn("pandas_datareader solo diario; se fuerza '1d'.")
                df = self.pdr.get_data_yahoo(symbol, start=start, end=end)
                if df is None or df.empty:
                    raise SymbolNotFound(
                        message=f"Símbolo no encontrado: {symbol}",
                        source="yahoo/pdr",
                        symbol=symbol,
                    )
                return df
            except Exception as e:
                last = e
                logger.exception("Fallo en pandas_datareader para %s", symbol)

        raise ExtractionError.from_http(
            message=f"Yahoo error descargando {symbol}",
            source="yahoo",
            symbol=symbol,
            status=None,
            headers=None,
            cause=last,
        )
