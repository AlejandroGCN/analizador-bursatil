from __future__ import annotations
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple, Union
from collections.abc import Iterable
import logging
import pandas as pd
from data_extractor.core.errors import ExtractionError

logger = logging.getLogger(__name__)

# Constantes para columnas OHLCV
ADJ_CLOSE_COL = "Adj Close"
REQUIRED_BASE_COLS = ["Open", "High", "Low", "Close", "Volume"]
REQUIRED_ALL_COLS = ["Open", "High", "Low", "Close", ADJ_CLOSE_COL, "Volume"]

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
    def _should_copy_dataframe(df: pd.DataFrame) -> bool:
        """Determina si el DataFrame necesita ser copiado antes de modificar."""
        return (not isinstance(df.index, pd.DatetimeIndex) or 
                df.index.tz is not None or 
                df.index.has_duplicates or
                not df.index.is_monotonic_increasing or
                any(col.title() != col for col in df.columns if col != ADJ_CLOSE_COL))
    
    @staticmethod
    def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los nombres de columnas a title-case sin perder 'Adj Close'."""
        rename_map = {c: c.title() for c in df.columns}
        if ADJ_CLOSE_COL in df.columns:
            rename_map[ADJ_CLOSE_COL] = ADJ_CLOSE_COL
        df.rename(columns=rename_map, inplace=True)
        return df
    
    @staticmethod
    def _ensure_ohlcv_structure(df: pd.DataFrame) -> pd.DataFrame:
        """Asegura que existan todas las columnas OHLCV requeridas."""
        for c in REQUIRED_BASE_COLS:
            if c not in df.columns:
                raise ExtractionError(f"Falta columna requerida: {c}", source="base")
        if ADJ_CLOSE_COL not in df.columns:
            df[ADJ_CLOSE_COL] = df["Close"]
        return df
    
    @staticmethod
    def _normalize_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza el índice a DatetimeIndex sin timezone."""
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index, utc=True)
            except Exception as ex:
                raise ExtractionError(f"Índice no convertible a fechas: {ex}", source="base")
        elif df.index.tz is not None:
            df.index = df.index.tz_convert("UTC").tz_localize(None)
        return df
    
    @staticmethod
    def _clean_and_sort_index(df: pd.DataFrame) -> pd.DataFrame:
        """Ordena el índice y elimina duplicados."""
        if not df.index.is_monotonic_increasing:
            df.sort_index(inplace=True)
        if df.index.has_duplicates:
            df = df[~df.index.duplicated(keep="first")]
        return df

    @staticmethod
    def _finalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza y valida un DataFrame OHLCV de forma eficiente."""
        if df is None or df.empty:
            raise ExtractionError("DataFrame vacío", source="base")
        
        # Solo copiar si necesitamos modificar
        should_copy = BaseAdapter._should_copy_dataframe(df)
        if should_copy:
            df = df.copy()

        # Pipeline de normalización
        df = BaseAdapter._normalize_column_names(df)
        df = BaseAdapter._ensure_ohlcv_structure(df)
        df = BaseAdapter._normalize_datetime_index(df)
        
        # Conversión numérica eficiente (vectorizada por columna)
        for col in REQUIRED_ALL_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Limpieza final
        df = BaseAdapter._clean_and_sort_index(df)
        
        # Reordenar columnas
        return df[REQUIRED_ALL_COLS]


    @staticmethod
    def _clip_range(df: pd.DataFrame, start: Optional[pd.Timestamp], end: Optional[pd.Timestamp]) -> pd.DataFrame:
        if start is not None:
            df = df[df.index >= pd.to_datetime(start)]
        if end is not None:
            df = df[df.index <= pd.to_datetime(end)]
        return df

    @staticmethod
    def _validate_ohlcv(df: pd.DataFrame) -> None:
        if list(df.columns) != REQUIRED_ALL_COLS:
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
        except (AttributeError, TypeError, ValueError, KeyError):
            # Ignorar errores de logging que no afectan funcionalidad
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

    def _normalize_symbols_input(
        self, 
        symbols: Union[Iterable[str], str, None]
    ) -> List[str]:
        """
        Normaliza la entrada de símbolos a una lista.
        
        Args:
            symbols: Símbolos en cualquier formato aceptable
            
        Returns:
            Lista normalizada de símbolos
            
        Raises:
            ExtractionError: Si la entrada es inválida
        """
        if symbols is None:
            raise ExtractionError("Debes proporcionar al menos un símbolo", source=self.name)

        if isinstance(symbols, str):
            return [symbols]
        
        try:
            norm_symbols = [s for s in symbols if s]  # type: ignore[union-attr]
        except TypeError as ex:
            raise ExtractionError(f"Símbolos no iterables: {ex}", source=self.name)
        
        if not norm_symbols:
            raise ExtractionError("Lista de símbolos vacía", source=self.name)
        
        return norm_symbols

    def _download_symbols_parallel(
        self,
        norm_symbols: List[str],
        start: Optional[Any],
        end: Optional[Any],
        interval: str,
        **options: Any
    ) -> Tuple[Dict[str, pd.DataFrame], List[Tuple[str, str]]]:
        """
        Descarga símbolos en paralelo usando ThreadPoolExecutor.
        
        Returns:
            Tupla con (resultados exitosos, errores)
        """
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

        return results, errors

    def _handle_download_errors(
        self,
        errors: List[Tuple[str, str]],
        results: Dict[str, pd.DataFrame],
        norm_symbols: List[str]
    ) -> None:
        """
        Maneja los errores de descarga y lanza excepciones apropiadas si es necesario.
        """
        # Si hay errores pero también hay resultados exitosos, registrar advertencia pero continuar
        if errors and results:
            logger.warning(
                "Algunos símbolos fallaron al descargar (%d errores de %d total): %s",
                len(errors), len(norm_symbols), [sym for sym, _ in errors]
            )
        
        # Solo lanzar excepción si TODOS los símbolos fallaron
        if not results and errors:
            sym, msg = errors[0]
            # Extraer el mensaje limpio sin los metadatos [source=...]
            clean_msg = msg.split('[source=')[0].strip() if '[source=' in msg else msg
            
            # Determinar si es SymbolNotFound o ExtractionError genérico
            if "No se encontraron datos" in msg or "not found" in msg.lower():
                from data_extractor.core.errors import SymbolNotFound
                raise SymbolNotFound(
                    f"No se encontraron datos para '{sym}' en {self.name}\n\n{clean_msg}",
                    source=self.name,
                    symbol=sym
                )
            
            raise ExtractionError(
                f"❌ No se pudieron descargar datos para '{sym}'\n\n{clean_msg}",
                source=self.name,
                symbol=sym
            )

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
        norm_symbols = self._normalize_symbols_input(symbols)
        results, errors = self._download_symbols_parallel(norm_symbols, start, end, interval, **options)
        self._handle_download_errors(errors, results, norm_symbols)
        return results
