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

        # Solo procesar si es necesario
        if not isinstance(df_raw.index, pd.DatetimeIndex) or df_raw.index.has_duplicates:
            df_raw = df_raw.copy()
            df_raw.index = pd.to_datetime(df_raw.index)
            df_raw.sort_index(inplace=True)
        elif not df_raw.index.is_monotonic_increasing:
            df_raw = df_raw.sort_index()

        for col in ["Open", "High", "Low", "Close"]:
            if col not in df_raw.columns:
                raise ExtractionError(
                    f"Columna esperada ausente en Stooq: {col}",
                    source=self.name,
                )
        if "Volume" not in df_raw.columns:
            df_raw["Volume"] = 0
        if ADJ_CLOSE_COL not in df_raw.columns:
            df_raw[ADJ_CLOSE_COL] = df_raw["Close"]

        df = df_raw[OHLCV_COLS]

        if interval in ("1wk", "1mo"):
            rule = "W-FRI" if interval == "1wk" else "M"
            agg_dict = {
                "Open":"first","High":"max","Low":"min",
                "Close":"last",ADJ_CLOSE_COL:"last","Volume":"sum"
            }
            df = (
                df.resample(rule)
                .agg(agg_dict)
                .dropna(how="any")
            )

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
