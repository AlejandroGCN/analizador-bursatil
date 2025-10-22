# core/base_adapter.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional, Any
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .errors import ExtractionError  # tus excepciones existentes

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """
    Clase base para adapters de mercado que descargan 1..N símbolos y
    devuelven DataFrames "brutos" (formato propio de la fuente).

    Proporciona:
    - normalización de la entrada (str o lista -> lista de símbolos)
    - ejecución paralela opcional para N símbolos
    - recogida de errores por símbolo
    - logging homogéneo
    """

    name: str = "abstract"          # sobrescribir en subclases
    supports_intraday: bool = True  # sobrescribir si aplica

    def __init__(self, *, timeout: int = 30, max_workers: int = 8, **kwargs: Any):
        self.timeout = timeout
        self.max_workers = max_workers
        self.extra_opts: Dict[str, Any] = dict(kwargs)
        logger.info(
            "%s init (timeout=%s, max_workers=%s, extra=%s)",
            self.__class__.__name__, timeout, max_workers, self.extra_opts
        )

    # ---------- helpers ----------
    @staticmethod
    def _normalize_symbols(symbols: Union[str, List[str]]) -> List[str]:
        if isinstance(symbols, str):
            return [s.strip() for s in symbols.split(",") if s.strip()]
        return [s.strip() for s in symbols if s and s.strip()]

    def get_symbols(
            self,
            symbols: Union[str, List[str]],
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str = "1d",
            **options: Any,
    ) -> Dict[str, pd.DataFrame]:
        """
        Descarga uno o varios símbolos desde la fuente concreta.
        Devuelve dict[symbol] -> DataFrame bruto.
        """
        sym_list = self._normalize_symbols(symbols)
        if not sym_list:
            logger.warning("get_symbols sin símbolos; usando demo AAPL.")
            sym_list = ["AAPL"]

        results: Dict[str, pd.DataFrame] = {}
        errors: Dict[str, Exception] = {}

        if len(sym_list) == 1:
            s = sym_list[0]
            results[s] = self.download_symbol(s, start, end, interval, **options)
            return results

        logger.info("Descargando %d símbolos desde %s...", len(sym_list), self.name)
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            fut_map = {
                ex.submit(self.download_symbol, s, start, end, interval, **options): s
                for s in sym_list
            }
            for fut in as_completed(fut_map):
                s = fut_map[fut]
                try:
                    results[s] = fut.result()
                except Exception as e:
                    errors[s] = e
                    logger.warning("Error descargando %s (%s): %s", s, self.name, e)

        if not results:
            raise ExtractionError(
                f"Falló la descarga de todos los símbolos en {self.name}: {errors}",
                source=self.name,
                extra={"errors": {k: str(v) for k, v in errors.items()}},
            )
        return results

    @abstractmethod
    def download_symbol(
            self,
            symbol: str,
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str,
            **options: Any,
    ) -> pd.DataFrame:
        """
        Descarga 1 símbolo y devuelve un DataFrame bruto en el formato
        propio de la fuente. Debe lanzar tus ExtractionError/SymbolNotFound
        cuando corresponda.
        """
        raise NotImplementedError
