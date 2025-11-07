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
    Fachada principal para la extracción de datos financieros desde múltiples fuentes.
    
    Esta clase actúa como punto de entrada unificado para acceder a datos bursátiles
    desde diferentes proveedores (Yahoo Finance, Binance, Tiingo). Proporciona una
    interfaz consistente independientemente de la fuente de datos utilizada.
    
    Características principales:
    - Resolución automática del provider basada en configuración
    - Normalización automática de datos a formatos estándar
    - Soporte para múltiples símbolos simultáneos
    - Manejo robusto de errores y timeouts
    - Configuración flexible de parámetros de extracción
    
    Attributes:
        cfg (ExtractorConfig): Configuración del extractor
        source (BaseProvider): Instancia del provider seleccionado
    
    Example:
        >>> # Configuración básica
        >>> extractor = DataExtractor()
        >>> data = extractor.get_market_data(['AAPL', 'MSFT'], start='2023-01-01')
        
        >>> # Configuración personalizada
        >>> config = ExtractorConfig(source='binance', timeout=60)
        >>> extractor = DataExtractor(config)
        >>> crypto_data = extractor.get_market_data(['BTCUSDT'], interval='1h')
    
    Note:
        Los datos devueltos están normalizados y listos para análisis.
        Cada serie temporal mantiene su formato original pero con estructura consistente.
    """

    def __init__(self, cfg: Optional[ExtractorConfig] = None):
        self.cfg = cfg or ExtractorConfig()
        logger.info("DataExtractor init cfg=%s", self.cfg)

        try:
            source_cls = REGISTRY[self.cfg.source]
        except KeyError as e:
            logger.error("Fuente no registrada en REGISTRY: %s", self.cfg.source)
            raise ValueError(f"Fuente no registrada: {self.cfg.source}") from e

        # Construir kwargs dinámicamente según configuración
        provider_kwargs = {"timeout": self.cfg.timeout}
        if self.cfg.api_key:
            provider_kwargs["api_key"] = self.cfg.api_key
        
        self.source = source_cls(**provider_kwargs)
        logger.info("Proveedor instanciado: %s", source_cls.__name__)

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
        Extrae datos de mercado para uno o múltiples símbolos financieros.
        
        Este método es el punto de entrada principal para obtener datos históricos
        de activos financieros. Soporta múltiples fuentes de datos y normaliza
        automáticamente los resultados a un formato estándar.
        
        Args:
            tickers: Símbolo(es) a extraer. Puede ser:
                - str: Un solo símbolo (ej: 'AAPL')
                - Iterable[str]: Múltiples símbolos (ej: ['AAPL', 'MSFT', 'GOOGL'])
            start: Fecha de inicio en formato flexible:
                - str: '2023-01-01', '2023-01-01 09:30:00'
                - pd.Timestamp: Timestamp de pandas
                - None: Usa fecha por defecto del provider
            end: Fecha de fin en formato flexible (mismo formato que start)
            interval: Resolución temporal de los datos:
                - '1d': Diario (por defecto)
                - '1h': Horario
                - '1wk': Semanal
                - '1mo': Mensual
                - '1m', '5m', '15m', '30m': Intradía (solo Yahoo)
                - None: Usa intervalo por defecto de configuración
            kind: Tipo de datos a extraer:
                - 'ohlcv': Precios OHLCV (Open, High, Low, Close, Volume)
                - 'returns_pct': Retornos porcentuales
                - 'returns_log': Retornos logarítmicos
            **params: Parámetros adicionales específicos del provider:
                - align: Estrategia de alineación ('intersect', 'union', None)
                - ffill: Forward fill para valores faltantes (bool)
                - bfill: Backward fill para valores faltantes (bool)
                - max_workers: Número de workers para requests paralelos (int)
        
        Returns:
            Dict[str, Any]: Diccionario con estructura:
                {
                    'symbol1': SerieObjeto1,
                    'symbol2': SerieObjeto2,
                    ...
                }
            
            Cada SerieObjeto es una instancia de la clase correspondiente al tipo
            solicitado (PriceSeries, PerformanceSeries, etc.) con datos normalizados.
        
        Raises:
            ValueError: Si no se proporcionan símbolos o el rango de fechas es inválido
            ExtractionError: Si falla la extracción de datos desde la fuente
            KeyError: Si la fuente especificada no está registrada
        
        Example:
            >>> extractor = DataExtractor()
            
            >>> # Datos básicos de una acción
            >>> data = extractor.get_market_data('AAPL', start='2023-01-01')
            >>> print(data['AAPL'].mean())  # Precio medio
            
            >>> # Múltiples símbolos con configuración personalizada
            >>> symbols = ['AAPL', 'MSFT', 'GOOGL']
            >>> data = extractor.get_market_data(
            ...     symbols, 
            ...     start='2023-01-01', 
            ...     end='2023-12-31',
            ...     interval='1d',
            ...     align='intersect',
            ...     ffill=True
            ... )
            
            >>> # Datos de criptomonedas desde Binance
            >>> config = ExtractorConfig(source='binance')
            >>> crypto_extractor = DataExtractor(config)
            >>> crypto_data = crypto_extractor.get_market_data(
            ...     ['BTCUSDT', 'ETHUSDT'], 
            ...     interval='1h',
            ...     kind='ohlcv'
            ... )
        
        Note:
            - Los datos se normalizan automáticamente según el tipo solicitado
            - Las fechas se alinean según la estrategia especificada
            - Los valores faltantes se manejan según los parámetros ffill/bfill
            - El método es thread-safe para múltiples símbolos
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
