from dataclasses import dataclass
from typing import Optional, Literal

# Definir el tipo SourceName fuera de la clase
# Nota: Stooq deprecado en favor de Tiingo (mejor cobertura y calidad)
SourceName = Literal["yahoo", "binance", "tiingo"]


@dataclass(slots=True, frozen=True)
class ExtractorConfig:
    """
    Configuración inmutable para el extractor de datos financieros.

    Esta clase centraliza todos los parámetros de configuración necesarios
    para la extracción de datos desde diferentes fuentes (Yahoo, Binance, Tiingo).
    Utiliza dataclass con slots=True para optimización de memoria y frozen=True
    para inmutabilidad.

    Attributes:
        source (SourceName): Fuente de datos a utilizar. Valores permitidos:
            - "yahoo": Yahoo Finance (gratuito, sin API key, cobertura global)
            - "binance": Binance API (criptomonedas, gratuito, alto límite)
            - "tiingo": Tiingo API (calidad institucional, 70+ exchanges, API key gratuita)
        timeout (int): Tiempo máximo de espera por petición HTTP en segundos.
            Valor por defecto: 30 segundos.
        interval (str): Intervalo temporal de los datos. Formatos soportados:
            - "1d": Diario (por defecto)
            - "1h": Horario
            - "1wk": Semanal
            - "1mo": Mensual
            - "1m", "5m", "15m", "30m": Intradía (solo Yahoo)
        ffill (bool): Si True, rellena valores faltantes hacia adelante
            (forward fill) tras la alineación de series múltiples.
            Valor por defecto: True.
        bfill (bool): Si True, rellena valores faltantes hacia atrás
            (backward fill). Usar con cautela ya que puede introducir
            sesgos en datos históricos. Valor por defecto: False.
        align (Optional[str]): Estrategia de alineación para series múltiples:
            - "intersect": Solo fechas comunes a todas las series (por defecto)
            - "union": Todas las fechas disponibles (puede crear NaN)
            - None: Sin alineación especial
        api_key (Optional[str]): Clave de API para fuentes que lo requieran.
            No necesario para Yahoo Finance. Valor por defecto: None.

    Example:
        >>> config = ExtractorConfig(
        ...     source="yahoo",
        ...     interval="1d",
        ...     timeout=60,
        ...     ffill=True
        ... )
        >>> print(config.source)
        yahoo
    """
    source: SourceName = "yahoo"
    timeout: int = 30
    interval: str = "1d"
    ffill: bool = True
    bfill: bool = False
    align: Optional[str] = "intersect"
    api_key: Optional[str] = None