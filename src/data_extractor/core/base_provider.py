# core/baseProvider.py
from __future__ import annotations

from typing import Optional, Dict, List, Any, Union
import logging
import pandas as pd

from .errors import DataSource, SeriesType          # Protocolo + unión de tipos
from .normalizer import normalizer_tipology       # Orquestador de normalización

logger = logging.getLogger(__name__)


class BaseProvider(DataSource):
    """
    Provider base: orquesta
      - adapter.get_symbols(...)  -> Dict[str, DataFrame] bruto
      - normalizer_tipology(...)  -> Dict[str, SeriesType] según 'kind'

    Subclases solo definen:
      - self.adapter   (inyectando el adapter concreto)
      - self.source_name (string corto de la fuente, p.ej. 'yahoo', 'alpha_vantage', 'binance')
    """

    def __init__(self, *, source_name: str, adapter: Any) -> None:
        self.source_name = source_name
        self.adapter = adapter
        logger.info("BaseProvider init source=%s adapter=%s", source_name, adapter.__class__.__name__)

    # ---------- helpers ----------
    @staticmethod
    def _normalize_symbols(symbols_input: Union[str, List[str]]) -> List[str]:
        if isinstance(symbols_input, str):
            symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
        else:
            # dedup conservando orden
            symbols = list(dict.fromkeys([s.strip() for s in symbols_input if s and s.strip()]))
        return symbols

    def get_symbols(
            self,
            symbols_input: Union[str, List[str]],
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
        symbols = self._normalize_symbols(symbols_input)
        logger.info(
            "%s.get_symbols symbols=%s start=%s end=%s interval=%s "
            "kind=%s align=%s ffill=%s bfill=%s",
            self.__class__.__name__, symbols, start, end, interval, kind, align, ffill, bfill
        )

        # 1) Descarga bruta desde el adapter (Dict[str, DataFrame])
        raw_map = self.adapter.get_symbols(symbols, start, end, interval)

        # 2) Normalización/Tipología destino (Dict[str, SeriesType])
        out = normalizer_tipology(
            raw_frames=raw_map,
            kind=kind,
            source_name=self.source_name,
            align=align,
            ffill=ffill,
            bfill=bfill,
            **options,
        )
        logger.info("%s.get_symbols -> OK %d símbolos (kind=%s)",
                    self.__class__.__name__, len(out), kind)
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
            "%s.get_data symbol=%s start=%s end=%s interval=%s "
            "kind=%s align=%s ffill=%s bfill=%s",
            self.__class__.__name__, symbol, start, end, interval, kind, align, ffill, bfill
        )
        out = self.get_symbols(
            symbols_input=[symbol],
            start=start,
            end=end,
            interval=interval,
            kind=kind,
            align=align,
            ffill=ffill,
            bfill=bfill,
            **options,
        )
        if symbol not in out:
            raise KeyError(f"Símbolo '{symbol}' no presente en salida normalizada.")
        return out[symbol]
