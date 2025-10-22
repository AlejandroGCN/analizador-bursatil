import warnings
from typing import Dict, List, Union
import pandas as pd
from importlib import util as importlib_util
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.base import SymbolNotFound, ExtractionError
import logging

logger = logging.getLogger(__name__)


class YahooAdapter:
    """
    Adapter para obtener datos desde Yahoo Finance.
    Acepta uno o varios símbolos de forma transparente.
    """

    def __init__(self, timeout: int = 30, max_workers: int = 8):
        self.timeout = timeout
        self.max_workers = max_workers
        logger.info("YahooAdapter init (timeout=%s, max_workers=%s)", timeout, max_workers)

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

    def download_symbol(self, symbol: str, start, end, interval: str) -> pd.DataFrame:
        last = None
        if self._yf:
            try:
                df = self.yf.download(symbol, start=start, end=end, interval=interval,
                                      progress=False, threads=False)
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

    def get_symbols(self, symbols: Union[str, List[str]], start, end, interval: str) -> Dict[str, pd.DataFrame]:
        """
        Descarga uno o varios símbolos de Yahoo Finance.
        Devuelve dict[symbol] -> DataFrame (formato Yahoo).
        """
        # Normaliza entrada
        if isinstance(symbols, str):
            symbols = [s.strip() for s in symbols.split(",") if s.strip()]
        if not symbols:
            logger.warning("get_symbols sin símbolos; usando demo AAPL.")
            symbols = ["AAPL"]

        results: Dict[str, pd.DataFrame] = {}
        errors: Dict[str, Exception] = {}

        if len(symbols) == 1:
            # Caso simple
            s = symbols[0]
            results[s] = self.download_symbol(s, start, end, interval)
            return results

        logger.info("Descargando %d símbolos desde Yahoo...", len(symbols))
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            fut_map = {ex.submit(self.download_symbol, s, start, end, interval): s for s in symbols}
            for fut in as_completed(fut_map):
                s = fut_map[fut]
                try:
                    results[s] = fut.result()
                except Exception as e:
                    errors[s] = e
                    logger.warning("Error descargando %s: %s", s, e)

        if not results:
            raise ExtractionError(f"Falló la descarga de todos los símbolos: {errors}")
        return results
