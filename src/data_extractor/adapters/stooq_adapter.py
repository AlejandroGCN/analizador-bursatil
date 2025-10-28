# src/data_extractor/adapters/stooq_adapter.py

from __future__ import annotations
from typing import Any, Optional
import logging
import pandas as pd
from data_extractor.core.base.base_adapter import BaseAdapter
from data_extractor.core.errors import ExtractionError, SymbolNotFound

logger = logging.getLogger(__name__)

# Constantes para columnas OHLCV
ADJ_CLOSE_COL = "Adj Close"
OHLCV_COLS = ["Open","High","Low","Close",ADJ_CLOSE_COL,"Volume"]

# Intentar importar pandas_datareader, si falla será opcional
try:
    from pandas_datareader import data as pdr
    _PDR_OK = True
except Exception:  # Captura cualquier error (ImportError, ModuleNotFoundError, etc.)
    _PDR_OK = False
    pdr = None

class StooqAdapter(BaseAdapter):
    name = "stooq"
    supports_intraday = False
    allowed_intervals = ["1d", "1wk", "1mo"]
    
    @staticmethod
    def _normalize_dataframe_index(df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza el índice del DataFrame a DatetimeIndex y lo ordena."""
        if not isinstance(df.index, pd.DatetimeIndex) or df.index.has_duplicates:
            df = df.copy()
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
        elif not df.index.is_monotonic_increasing:
            df = df.sort_index()
        return df
    
    @staticmethod
    def _ensure_ohlcv_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Valida y crea las columnas OHLCV necesarias."""
        for col in ["Open", "High", "Low", "Close"]:
            if col not in df.columns:
                raise ExtractionError(
                    f"Columna esperada ausente en Stooq: {col}",
                    source="stooq",
                )
        if "Volume" not in df.columns:
            df["Volume"] = 0
        if ADJ_CLOSE_COL not in df.columns:
            df[ADJ_CLOSE_COL] = df["Close"]
        return df
    
    @staticmethod
    def _resample_by_interval(df: pd.DataFrame, interval: str) -> pd.DataFrame:
        """Resample el DataFrame si el intervalo es 1wk o 1mo."""
        if interval not in ("1wk", "1mo"):
            return df
        
        rule = "W-FRI" if interval == "1wk" else "M"
        agg_dict = {
            "Open":"first","High":"max","Low":"min",
            "Close":"last",ADJ_CLOSE_COL:"last","Volume":"sum"
        }
        return df.resample(rule).agg(agg_dict).dropna(how="any")

    def download_symbol(
            self,
            symbol: str,
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str,
            **options: Any,
    ) -> pd.DataFrame:
        if not _PDR_OK:
            raise ExtractionError(
                "pandas_datareader no está disponible (incompatible con Python 3.12+). "
                "Stooq no está soportado en esta versión de Python. "
                "Usa Yahoo o Binance como alternativa.",
                source=self.name
            )
        if interval not in self.allowed_intervals:
            raise ExtractionError(
                f"Intervalo '{interval}' no soportado por Stooq (usa 1d/1wk/1mo).",
                source=self.name
            )

        logger.info("Descargando %s con intervalo %s desde Stooq", symbol, interval)

        try:
            df_raw = pdr.DataReader(
                name=symbol,
                data_source="stooq",
                start=start,
                end=end,
            )
        except Exception as e:
            raise ExtractionError(
                f"Error accediendo a Stooq para {symbol}",
                source=self.name
            ) from e

        if df_raw is None or df_raw.empty:
            raise SymbolNotFound(
                message=f"Sin datos en Stooq para: {symbol}",
                source=self.name,
            )

        # Normalizar índice y columnas usando funciones auxiliares
        df_raw = self._normalize_dataframe_index(df_raw)
        df_raw = self._ensure_ohlcv_columns(df_raw)
        df = df_raw[OHLCV_COLS]
        df = self._resample_by_interval(df, interval)

        df = self._clip_range(df, start, end)
        df = self._finalize_ohlcv(df)
        self._validate_ohlcv(df)

        sample = df.head(20)
        logger.info(
            "[%s] %d filas normalizadas, rango %s → %s\n%s",
            symbol, len(df), df.index.min(), df.index.max(),
            sample.to_string()
        )
        return df
