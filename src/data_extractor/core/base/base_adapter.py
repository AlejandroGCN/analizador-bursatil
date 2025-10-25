from __future__ import annotations
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple, Union
from collections.abc import Iterable
import logging
import pandas as pd
from data_extractor.core.errors import ExtractionError

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    """
    Clase base para adapters de datos OHLCV.
    Los adapters concretos deben implementar download_symbol() y devolver
    un DataFrame con columnas: Open, High, Low, Close, Adj Close, Volume
    indexado por DatetimeIndex ascendente.
    """
    name: str = "base"
    supports_intraday: bool = True
    allowed_intervals: List[str] = ["1d"]

    def __init__(self, timeout: int = 30, max_workers: int = 8) -> None:
        self.timeout = timeout
        self.max_workers = max_workers

    # ------------------------ utilidades comunes ------------------------

    @staticmethod
    def _finalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            raise ExtractionError("DataFrame vacío", source="base")
        # Solo copiar si necesitamos modificar
        if (not isinstance(df.index, pd.DatetimeIndex) or 
            df.index.tz is not None or 
            df.index.has_duplicates or
            not df.index.is_monotonic_increasing or
            any(col.title() != col for col in df.columns if col != "Adj Close")):
            df = df.copy()

        # 1) Normaliza nombres (title-case) sin perder "Adj Close"
        rename_map = {c: c.title() for c in df.columns}
        if "Adj Close" in df.columns:  # asegura preservación exacta
            rename_map["Adj Close"] = "Adj Close"
        df.rename(columns=rename_map, inplace=True)

        # 2) Asegura columnas base y crea Adj Close si falta
        required = ["Open", "High", "Low", "Close", "Volume"]
        for c in required:
            if c not in df.columns:
                raise ExtractionError(f"Falta columna requerida: {c}", source="base")
        if "Adj Close" not in df.columns:
            df["Adj Close"] = df["Close"]

        # 3) Índice temporal (tz coherente)
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index, utc=True)
            except Exception as ex:
                raise ExtractionError(f"Índice no convertible a fechas: {ex}", source="base")
        elif df.index.tz is not None:
            df.index = df.index.tz_convert("UTC").tz_localize(None)

        # 4) Tipos numéricos + limpieza de no-finitos
        for c in ["Open","High","Low","Close","Adj Close","Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        # 5) Orden y duplicados
        if not df.index.is_monotonic_increasing:
            df.sort_index(inplace=True)
        if df.index.has_duplicates:
            df = df[~df.index.duplicated(keep="first")]

        # 6) Reordena columnas
        cols = ["Open","High","Low","Close","Adj Close","Volume"]
        df = df[cols]

        return df


    @staticmethod
    def _clip_range(df: pd.DataFrame, start: Optional[pd.Timestamp], end: Optional[pd.Timestamp]) -> pd.DataFrame:
        if start is not None:
            df = df[df.index >= pd.to_datetime(start)]
        if end is not None:
            df = df[df.index <= pd.to_datetime(end)]
        return df

    @staticmethod
    def _validate_ohlcv(df: pd.DataFrame) -> None:
        cols = ["Open","High","Low","Close","Adj Close","Volume"]
        if list(df.columns) != cols:
            raise ExtractionError(f"Columnas inválidas: {list(df.columns)}", source="base")
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ExtractionError("Índice debe ser DatetimeIndex", source="base")
        if not df.index.is_monotonic_increasing:
            raise ExtractionError("Índice no está en orden ascendente", source="base")

    @staticmethod
    def _log_df_summary(df: pd.DataFrame, symbol: str) -> None:
        try:
            logger.info("[%s] filas=%d desde=%s hasta=%s",
                        symbol, len(df),
                        None if df.empty else df.index.min(),
                        None if df.empty else df.index.max())
        except Exception:
            pass

    # ------------------------ API pública ------------------------

    @abstractmethod
    def download_symbol(
            self,
            symbol: str,
            start: Optional[Any],
            end: Optional[Any],
            interval: str,
            **options: Any
    ) -> pd.DataFrame:
        """
        Debe devolver un DataFrame OHLCV normalizado.
        """
        raise NotImplementedError

    def get_symbols(
            self,
            symbols: Union[Iterable[str], str, None],
            start: Optional[Any],
            end: Optional[Any],
            interval: str,
            **options: Any
    ) -> Dict[str, pd.DataFrame]:
        """
        Descarga en paralelo múltiples símbolos. Acepta lista/tupla/conjunto o un string único.
        Rechaza None o colecciones vacías.
        """
        # normaliza entrada
        if symbols is None:
            raise ExtractionError("Debes proporcionar al menos un símbolo", source=self.name)

        if isinstance(symbols, str):
            norm_symbols = [symbols]
        else:
            try:
                norm_symbols = [s for s in symbols if s]  # type: ignore[union-attr]
            except TypeError as ex:
                raise ExtractionError(f"Símbolos no iterables: {ex}", source=self.name)
            if not norm_symbols:
                raise ExtractionError("Lista de símbolos vacía", source=self.name)

        results: Dict[str, pd.DataFrame] = {}
        errors: List[Tuple[str, str]] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            fut_map = {
                pool.submit(self.download_symbol, s, start, end, interval, **options): s
                for s in norm_symbols
            }
            for fut in as_completed(fut_map):
                sym = fut_map[fut]
                try:
                    df = fut.result()
                    self._validate_ohlcv(df)
                    self._log_df_summary(df, sym)
                    results[sym] = df
                except Exception as ex:
                    errors.append((sym, str(ex)))
                    logger.warning("Fallo descargando %s: %s", sym, ex)

        if not results and errors:
            sym, msg = errors[0]
            raise ExtractionError(f"Todos fallaron. Ej. {sym}: {msg}", source=self.name)

        return results
