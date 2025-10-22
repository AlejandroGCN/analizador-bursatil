from dataclasses import dataclass
from typing import Optional, Literal


@dataclass(slots=True, frozen=True)
class ExtractorConfig:
    """
    ---------
    source: str
    Nombre de la fuente (p. ej. 'yahoo').
    timeout: int
    Tiempo máximo de espera por petición en segundos.
    interval: str
    Intervalo temporal (dependiente de la fuente). Ej.: '1d', '1wk', '1mo'.
    ffill: bool
    Si True, rellena huecos hacia adelante tras la alineación.
    bfill: bool
    Si True, rellena huecos hacia atrás (usar con cautela).
    align: Optional[str]
    Alineación entre series múltiples: None | 'intersect' | 'union'.
    api_key: Optional[str]
    Clave de API para fuentes que lo requieran (no aplicable a Yahoo por defecto).
    """
    SourceName = Literal["yahoo", "alpha_vantage", "binance"]
    timeout: int = 30
    interval: str = "1d"
    ffill: bool = True
    bfill: bool = False
    align: Optional[str] = "intersect"
    api_key: Optional[str] = None