# src/data_extractor/extractor.py
from typing import Dict, Iterable, Optional
import logging
import pandas as pd

from .config import ExtractorConfig
from .core.base import ExtractionError
from .core.registry import REGISTRY

logger = logging.getLogger(__name__)

def _ensure_dt(x):
    """Convierte entrada flexible de fecha a `pd.Timestamp` o `None`."""
    return None if x is None else pd.to_datetime(x)

class DataExtractor:
    """
    Fachada de alto nivel:
    - Resuelve el provider desde REGISTRY (p. ej. YahooProvider).
    - Llama al provider.get_symbols(), que se encarga de todo (adapter + normalizer).
    - Devuelve dict[symbol -> objeto tipología].
    """

    def __init__(self, cfg: Optional[ExtractorConfig] = None):
        self.cfg = cfg or ExtractorConfig()
        logger.info("DataExtractor init cfg=%s", self.cfg)

        try:
            source_cls = REGISTRY[self.cfg.source]
        except KeyError as e:
            logger.error("Fuente no registrada: %s", self.cfg.source)
            raise ValueError(f"Fuente no registrada: {self.cfg.source}") from e

        self.source = source_cls(timeout=self.cfg.timeout)
        logger.info("Proveedor instanciado: %s", source_cls.__name__)

    def get_market_data(
            self,
            tickers: Iterable[str] | str,
            start: Optional[str | pd.Timestamp] = None,
            end: Optional[str | pd.Timestamp] = None,
            interval: Optional[str] = None,
            kind: str = "ohlcv",
            **params,
    ) -> Dict[str, object]:
        """
        Descarga 1..N símbolos usando el provider.
        El provider maneja el adapter y normalizer internamente.
        """
        symbols = [tickers] if isinstance(tickers, str) else list(dict.fromkeys(tickers))
        start_ts = _ensure_dt(start)
        end_ts = _ensure_dt(end)
        interval = interval or self.cfg.interval

        logger.info(
            "get_market_data: symbols=%s start=%s end=%s interval=%s kind=%s align=%s ffill=%s bfill=%s",
            symbols, start_ts, end_ts, interval, kind, self.cfg.align, self.cfg.ffill, self.cfg.bfill
        )

        try:
            # 👉 El provider (p. ej. YahooProvider) implementa get_symbols()
            # que usa internamente el adapter + normalizer_tipology()
            return self.source.get_symbols(
                symbols_input=symbols,
                start=start_ts,
                end=end_ts,
                interval=interval,
                kind=kind,
                align=self.cfg.align,
                ffill=self.cfg.ffill,
                bfill=self.cfg.bfill,
                **params,
            )
        except Exception as e:
            logger.exception("Fallo en provider.get_symbols")
            raise ExtractionError(f"Fallo en extracción: {e}") from e
