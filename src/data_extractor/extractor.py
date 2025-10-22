# src/data_extractor/extractor.py
from typing import Dict, Iterable, Optional, Any, List
import logging
import pandas as pd

from .config import ExtractorConfig
from .core.errors import ExtractionError
from .core.registry import REGISTRY

logger = logging.getLogger(__name__)


def _ensure_dt(x) -> Optional[pd.Timestamp]:
    """Convierte entrada flexible de fecha a `pd.Timestamp` o `None`."""
    return None if x is None else pd.to_datetime(x)


class DataExtractor:
    """
    Fachada de alto nivel:
      - Resuelve el provider desde REGISTRY (p. ej. YahooProvider).
      - Llama al provider.get_symbols(), que se encarga de adapter + normalizer.
      - Devuelve dict[symbol -> tipología/objeto listo].
    """

    def __init__(self, cfg: Optional[ExtractorConfig] = None):
        self.cfg = cfg or ExtractorConfig()
        logger.info("DataExtractor init cfg=%s", self.cfg)

        try:
            source_cls = REGISTRY[self.cfg.source]
        except KeyError as e:
            logger.error("Fuente no registrada en REGISTRY: %s", self.cfg.source)
            raise ValueError(f"Fuente no registrada: {self.cfg.source}") from e

        # Instancia del provider (pasa args comunes si aplica).
        self.source = source_cls(timeout=self.cfg.timeout)
        logger.info("Proveedor instanciado: %s", getattr(source_cls, "__name__", str(source_cls)))

    def get_market_data(
            self,
            tickers: Iterable[str] | str,
            start: Optional[str | pd.Timestamp] = None,
            end: Optional[str | pd.Timestamp] = None,
            interval: Optional[str] = None,
            kind: str = "ohlcv",
            **params: Any,
    ) -> Dict[str, Any]:
        """
        Descarga 1..N símbolos usando el provider (quien maneja adapter y normalizer).

        Args:
            tickers: Iterable de símbolos o una cadena con un solo símbolo.
            start: fecha inicio (str/Timestamp/None).
            end: fecha fin (str/Timestamp/None).
            interval: resolución temporal; si None usa cfg.interval.
            kind: tipología (p. ej. 'ohlcv').
            **params: extras soportados por el provider (align, ffill, bfill, etc.).

        Returns:
            Dict[str, Any]: mapa símbolo -> objeto tipología ya normalizado por el provider.
        """
        # Normaliza símbolos preservando orden y eliminando duplicados
        if isinstance(tickers, str):
            symbols: List[str] = [tickers]
        else:
            symbols = list(dict.fromkeys(tickers))

        if not symbols:
            raise ValueError("Debe indicar al menos un símbolo.")

        start_ts = _ensure_dt(start)
        end_ts = _ensure_dt(end)
        chosen_interval = interval or self.cfg.interval

        if start_ts and end_ts and start_ts > end_ts:
            raise ValueError(f"Rango de fechas inválido: start({start_ts}) > end({end_ts}).")

        # Extra comunes de configuración si el caller no los pasa
        params.setdefault("align", self.cfg.align)
        params.setdefault("ffill", self.cfg.ffill)
        params.setdefault("bfill", self.cfg.bfill)

        logger.info(
            "get_market_data: symbols=%s start=%s end=%s interval=%s kind=%s align=%s ffill=%s bfill=%s",
            symbols, start_ts, end_ts, chosen_interval, kind,
            params.get("align"), params.get("ffill"), params.get("bfill"),
        )

        try:
            return self.source.get_symbols(
                symbols=symbols,
                start=start_ts,
                end=end_ts,
                interval=chosen_interval,
                kind=kind,
                **params,
            )
        except ExtractionError:
            logger.exception("Fallo en provider.get_symbols (ExtractionError)")
            raise
        except Exception as e:
            logger.exception("Fallo en provider.get_symbols (error no tipificado)")
            raise ExtractionError(f"Fallo en extracción: {e}") from e
