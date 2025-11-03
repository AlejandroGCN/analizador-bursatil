# core/baseProvider.py
from __future__ import annotations

from typing import Optional, Dict, List, Any, Union
import logging
import pandas as pd

# Importa tus clases de series normalizadas
from data_extractor.series import (
    PriceSeries,
    PerformanceSeries,
    VolumeActivitySeries,
    VolatilitySeries,
)
from data_extractor.core.errors import ExtractionError
from data_extractor.core.normalizer import normalizer_tipology  # Orquestador de normalización

logger = logging.getLogger(__name__)

# Alias de tipo: cualquier serie normalizada que pueda devolver el normalizador
SeriesType = Union[PriceSeries, PerformanceSeries, VolumeActivitySeries, VolatilitySeries]


class BaseProvider:
    """
    Provider base: orquesta
      - adapter.get_symbols(...)  -> Dict[str, DataFrame] bruto
      - normalizer_tipology(...)  -> Dict[str, SeriesType] según 'kind'

    Subclases solo definen:
      - self.adapter      (inyectando el adapter concreto)
      - self.source_name  (string corto: 'yahoo', 'binance', 'tiingo')
    """

    def __init__(self, *, source_name: str, adapter: Any) -> None:
        self.source_name = source_name
        self.adapter = adapter
        logger.info(
            "BaseProvider init source=%s adapter=%s",
            source_name,
            adapter.__class__.__name__,
        )

    # ---------- helpers ----------
    @staticmethod
    def _normalize_symbols(symbols: Union[str, List[str], None]) -> List[str]:
        """
        Acepta None, str o lista y devuelve lista limpia (sin vacíos ni duplicados, conservando orden).
        Soporta ',' y ';' como separadores.
        """
        if symbols is None:
            return []

        if isinstance(symbols, str):
            # permite ; además de ,
            s = symbols.replace(";", ",")
            parts = [p.strip() for p in s.split(",") if p.strip()]
        else:
            parts = [str(p).strip() for p in symbols if p and str(p).strip()]

        seen: set[str] = set()
        result: List[str] = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                result.append(p)
        return result

    # ---------- API principal ----------
    def get_symbols(
            self,
            symbols: Union[str, List[str], None],
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str = "1d",
            *,
            kind: str = "ohlcv",
            align: Optional[str] = None,
            ffill: bool = False,
            bfill: bool = False,
            **options: Any,
    ) -> Dict[str, SeriesType]:
        """
        Descarga (adapter) y normaliza (normalizer_tipology) 1..N símbolos.
        Devuelve {symbol -> objeto SeriesType} acorde a 'kind'.
        """
        norm_symbols = self._normalize_symbols(symbols)
        logger.info(
            "%s.get_symbols symbols=%s start=%s end=%s interval=%s kind=%s align=%s ffill=%s bfill=%s",
            self.__class__.__name__,
            norm_symbols,
            start,
            end,
            interval,
            kind,
            align,
            ffill,
            bfill,
        )

        if not norm_symbols:
            msg = "Debe introducir al menos un símbolo para obtener datos y realizar la simulación."
            logger.error("%s.get_symbols falló: %s", self.__class__.__name__, msg)
            raise ExtractionError(
                msg, source=self.source_name, extra={"input_symbols": symbols}
            )

        # 1) Descarga bruta desde el adapter (Dict[str, DataFrame])
        raw_map = self.adapter.get_symbols(norm_symbols, start, end, interval, **options)

        # 2) Normalización/Tipología destino (Dict[str, SeriesType])
        out: Dict[str, SeriesType] = normalizer_tipology(
            raw_frames=raw_map,
            kind=kind,
            source_name=self.source_name,
            align=align or "union",
            ffill=ffill,
            bfill=bfill,
            **options,
        )
        logger.info(
            "%s.get_symbols -> OK %d símbolos (kind=%s)",
            self.__class__.__name__,
            len(out),
            kind,
        )
        return out

    def get_data(
            self,
            symbol: str,
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str = "1d",
            *,
            kind: str = "ohlcv",
            align: Optional[str] = None,
            ffill: bool = False,
            bfill: bool = False,
            **options: Any,
    ) -> SeriesType:
        """
        Atajo para un único símbolo: llama a get_symbols y extrae el objeto.
        """
        logger.info(
            "%s.get_data symbol=%s start=%s end=%s interval=%s kind=%s align=%s ffill=%s bfill=%s",
            self.__class__.__name__,
            symbol,
            start,
            end,
            interval,
            kind,
            align,
            ffill,
            bfill,
        )

        norm_list = self._normalize_symbols([symbol])
        if not norm_list:
            msg = "Debe introducir al menos un símbolo para obtener datos y realizar la simulación."
            logger.error("%s.get_data falló: %s", self.__class__.__name__, msg)
            raise ExtractionError(
                msg, source=self.source_name, extra={"input_symbol": symbol}
            )

        norm_symbol = norm_list[0]
        out = self.get_symbols(
            symbols=norm_symbol,
            start=start,
            end=end,
            interval=interval,
            kind=kind,
            align=align,
            ffill=ffill,
            bfill=bfill,
            **options,
        )

        if norm_symbol not in out:
            raise KeyError(
                f"Símbolo '{norm_symbol}' no presente en salida normalizada."
            )
        return out[norm_symbol]
