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
    Clase base para adapters de mercado que descargan uno o varios símbolos y
    devuelven DataFrames.

    Proporciona:
        - Normalización de la entrada (lista o string)
        - Ejecución paralela para múltiples símbolos
        - Manejo uniforme de errores
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
        """
        Acepta una cadena o lista de símbolos y devuelve una lista limpia.
        """
        if isinstance(symbols, str):
            return [s.strip() for s in symbols.split(",") if s.strip()]
        return [s.strip() for s in symbols if s and s.strip()]

    def get_symbols(
            self,
            symbols: Union[str, List[str], None],
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str = "1d",
            **options: Any,
    ) -> Dict[str, pd.DataFrame]:
        """
        Descarga uno o varios símbolos desde la fuente concreta.
        Devuelve dict[symbol] -> DataFrame.
        """
        sym_list = self._normalize_symbols(symbols) if symbols else []

        if not sym_list:
            # 🚨 Error crítico: no se ha introducido ningún símbolo
            msg = (
                "Debe introducir al menos un símbolo para obtener datos "
                "y realizar la simulación."
            )
            logger.error("get_symbols falló: %s", msg)
            raise ExtractionError(
                msg,
                source=self.name,
                extra={"input_symbols": symbols}
            )

        results: Dict[str, pd.DataFrame] = {}
        errors: Dict[str, Exception] = {}

        if len(sym_list) == 1:
            s = sym_list[0]
            logger.info("Descargando símbolo único: %s (%s)", s, self.name)
            results[s] = self.download_symbol(s, start, end, interval, **options)
            return results

        # Ejecución paralela
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
                f"Falló la descarga de todos los símbolos en {self.name}.",
                source=self.name,
                extra={"errors": {k: str(v) for k, v in errors.items()}},
            )

        return results

    # ---------- método abstracto ----------
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
        propio de la fuente. Debe lanzar ExtractionError o SymbolNotFound
        cuando corresponda.
        """
        raise NotImplementedError
