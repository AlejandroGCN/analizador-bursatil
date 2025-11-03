from __future__ import annotations
import logging
import pandas as pd
import requests
from typing import Optional
from data_extractor.core.base.base_adapter import BaseAdapter
from data_extractor.core.errors import ExtractionError

logger = logging.getLogger(__name__)

# Constantes para columnas OHLCV
ADJ_CLOSE_COL = "Adj Close"
REQUIRED_OHLCV_COLS = ["Open", "High", "Low", "Close", ADJ_CLOSE_COL, "Volume"]


class TiingoAdapter(BaseAdapter):
    """
    Adaptador para Tiingo API.
    
    Tiingo ofrece datos de calidad institucional para más de 70 exchanges globales.
    Requiere API key gratuita de https://www.tiingo.com/
    
    Límites Free Tier:
    - 1000 símbolos únicos por día
    - 500 requests por hora
    - Datos end-of-day (EOD)
    
    Cobertura:
    - USA: NYSE, NASDAQ, AMEX
    - Internacional: LSE, TSX, ASX, y más
    - Datos históricos hasta 30+ años
    """
    
    name = "tiingo"
    supports_intraday = False  # Free tier solo soporta datos diarios
    allowed_intervals = ["1d"]  # Solo daily data en free tier
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        timeout: int = 30, 
        max_workers: int = 8
    ) -> None:
        """
        Inicializa TiingoAdapter.
        
        Args:
            api_key: API key de Tiingo (obtener en tiingo.com)
            timeout: Timeout para requests en segundos
            max_workers: Número de workers para descarga paralela
        """
        super().__init__(timeout=timeout, max_workers=max_workers)
        
        # Intentar obtener API key de variable de entorno si no se proporciona
        if api_key is None:
            import os
            api_key = os.environ.get("TIINGO_API_KEY")
        
        if not api_key:
            raise ValueError(
                "API key de Tiingo requerida. "
                "Consulta CONFIGURACION_API_KEYS.md para obtener instrucciones detalladas. "
                "Registro gratuito en: https://www.tiingo.com/"
            )
        
        self.api_key = api_key
        self.base_url = "https://api.tiingo.com/tiingo/daily"
        
        logger.info(
            "TiingoAdapter inicializado (timeout=%s, max_workers=%s)",
            timeout, max_workers
        )
    
    def _fetch_data(self, symbol: str, start: str, end: str) -> list[dict]:
        """
        Hace la petición HTTP a Tiingo API.
        
        Args:
            symbol: Símbolo del ticker (ej: 'AAPL', 'MSFT')
            start: Fecha inicio formato YYYY-MM-DD
            end: Fecha fin formato YYYY-MM-DD
            
        Returns:
            Lista de diccionarios con datos OHLCV
            
        Raises:
            ExtractionError: Si falla la petición o no hay datos
        """
        url = f"{self.base_url}/{symbol}/prices"
        
        params = {
            'startDate': start,
            'endDate': end,
            'token': self.api_key,
            'format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) == 0:
                raise ExtractionError(
                    f"No se encontraron datos para '{symbol}' en Tiingo",
                    source=self.name,
                    symbol=symbol
                )
            
            logger.debug(
                "[%s] Descargados %d registros de Tiingo API", 
                symbol, len(data)
            )
            
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ExtractionError(
                    f"Símbolo '{symbol}' no encontrado en Tiingo",
                    source=self.name,
                    symbol=symbol
                )
            elif e.response.status_code == 401:
                raise ExtractionError(
                    "API key de Tiingo inválida o expirada",
                    source=self.name,
                    symbol=symbol
                )
            elif e.response.status_code == 429:
                raise ExtractionError(
                    "Límite de rate de Tiingo excedido (500 req/hora)",
                    source=self.name,
                    symbol=symbol
                )
            else:
                raise ExtractionError(
                    f"Error HTTP al consultar Tiingo: {e}",
                    source=self.name,
                    symbol=symbol
                )
                
        except requests.exceptions.Timeout:
            raise ExtractionError(
                f"Timeout al consultar Tiingo para '{symbol}'",
                source=self.name,
                symbol=symbol
            )
            
        except Exception as e:
            raise ExtractionError(
                f"Error inesperado al consultar Tiingo: {e}",
                source=self.name,
                symbol=symbol
            )
    
    def _parse_to_dataframe(self, data: list[dict], symbol: str) -> pd.DataFrame:
        """
        Convierte la respuesta JSON de Tiingo a DataFrame.
        
        Formato de respuesta Tiingo:
        [
            {
                "date": "2024-01-01T00:00:00.000Z",
                "close": 150.5,
                "high": 152.0,
                "low": 149.0,
                "open": 151.0,
                "volume": 1000000,
                "adjClose": 150.5,
                "adjHigh": 152.0,
                "adjLow": 149.0,
                "adjOpen": 151.0,
                "adjVolume": 1000000,
                "divCash": 0.0,
                "splitFactor": 1.0
            },
            ...
        ]
        
        Args:
            data: Lista de diccionarios de Tiingo
            symbol: Símbolo del ticker
            
        Returns:
            DataFrame con índice DatetimeIndex y columnas OHLCV
        """
        df = pd.DataFrame(data)
        
        # Convertir fecha a datetime y establecer como índice
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Renombrar columnas al formato estándar OHLCV
        # Usar valores ajustados (adjOpen, adjClose, etc.) para consistencia
        column_mapping = {
            'adjOpen': 'Open',
            'adjHigh': 'High',
            'adjLow': 'Low',
            'adjClose': 'Close',
            'adjVolume': 'Volume'
        }
        
        # Si no hay columnas ajustadas, usar las regulares
        if 'adjClose' not in df.columns:
            column_mapping = {
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Añadir columna Adj Close (Tiingo ya proporciona datos ajustados)
        df[ADJ_CLOSE_COL] = df['Close']
        
        # Seleccionar solo columnas requeridas
        df = df[REQUIRED_OHLCV_COLS]
        
        logger.debug(
            "[%s] DataFrame creado: %d filas, rango %s → %s",
            symbol, len(df), df.index.min(), df.index.max()
        )
        
        return df
    
    def download_symbol(
        self, 
        symbol: str, 
        start: str, 
        end: str, 
        interval: str = "1d",
        **options
    ) -> pd.DataFrame:
        """
        Descarga datos históricos de un símbolo desde Tiingo.
        
        Args:
            symbol: Símbolo del ticker (ej: 'AAPL', 'GOOGL')
            start: Fecha inicio formato YYYY-MM-DD
            end: Fecha fin formato YYYY-MM-DD
            interval: Intervalo (solo '1d' soportado en free tier)
            **options: Opciones adicionales (ignoradas)
            
        Returns:
            DataFrame con columnas OHLCV normalizadas
            
        Raises:
            ExtractionError: Si hay algún error en la descarga o procesamiento
        """
        if interval not in self.allowed_intervals:
            raise ExtractionError(
                f"Intervalo '{interval}' no soportado. "
                f"Tiingo free tier solo soporta: {self.allowed_intervals}",
                source=self.name
            )
        
        logger.info(
            "[%s] Descargando de Tiingo: %s → %s (intervalo=%s)",
            symbol, start, end, interval
        )
        
        # Fetch data from API
        raw_data = self._fetch_data(symbol, start, end)
        
        # Parse to DataFrame
        df = self._parse_to_dataframe(raw_data, symbol)
        
        # Normalización estándar de BaseAdapter
        df = self._finalize_ohlcv(df)
        
        # Recortar al rango solicitado
        df = self._clip_range(df, start, end)
        
        # Validar datos OHLCV
        self._validate_ohlcv(df)
        
        # Log de muestra
        sample = df.head(20)
        logger.info(
            "[%s] %d filas normalizadas de Tiingo, rango %s → %s\n%s",
            symbol, len(df), df.index.min(), df.index.max(),
            sample.to_string()
        )
        
        return df

