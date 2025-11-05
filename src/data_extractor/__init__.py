"""
Módulo de extracción de datos financieros.

Proporciona una interfaz unificada para acceder a datos de mercado desde
múltiples fuentes (Yahoo Finance, Binance, Tiingo). El módulo maneja
automáticamente la descarga, normalización y validación de datos.

Classes:
    DataExtractor: Clase principal para extracción de datos
    ExtractorConfig: Configuración del extractor

Example:
    >>> from data_extractor import DataExtractor
    >>> extractor = DataExtractor()
    >>> data = extractor.get_market_data(['AAPL', 'MSFT'], start='2023-01-01')
"""
from .extractor import DataExtractor
from .config import ExtractorConfig

__all__ = ["DataExtractor", "ExtractorConfig"]