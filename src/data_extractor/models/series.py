# src/models/series.py
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

@dataclass
class PriceSeries:
    """
    Representa una serie temporal de precios OHLCV ya normalizada.
    Calcula automáticamente media y desviación típica del precio de cierre.
    """
    symbol: str
    source: str
    data: pd.DataFrame
    mean_close: float = field(init=False)
    std_close: float = field(init=False)

    def __post_init__(self):
        """Cálculos automáticos sobre los datos normalizados."""
        if self.data.empty:
            self.mean_close = np.nan
            self.std_close = np.nan
            return

        # Seguridad mínima: asegurar columna 'close'
        if "close" not in self.data.columns:
            raise ValueError("El DataFrame normalizado debe incluir la columna 'close'.")

        close = pd.to_numeric(self.data["close"], errors="coerce")
        self.mean_close = float(close.mean())
        self.std_close = float(close.std(ddof=1))

    # Métodos explícitos
    def mean(self) -> float:
        """Media del precio de cierre."""
        return self.mean_close

    def std(self) -> float:
        """Desviación típica del precio de cierre."""
        return self.std_close

    def describe(self) -> pd.DataFrame:
        """Resumen estadístico completo."""
        return self.data.describe()

    def tail(self, n: int = 5) -> pd.DataFrame:
        """Últimos n registros."""
        return self.data.tail(n)

@dataclass
class PerformanceSeries:
    """
    Serie 1D de rendimientos (pct o log) derivada del 'close'.
    Calcula automáticamente media y desviación típica de los retornos.
    """
    symbol: str
    source: str
    data: pd.Series            # columna única de retornos
    kind: str                  # "returns_pct" | "returns_log"
    mean_ret: float = field(init=False)
    std_ret: float = field(init=False)

    def __post_init__(self):
        s = pd.to_numeric(self.data, errors="coerce")
        if s.empty:
            self.mean_ret = np.nan
            self.std_ret = np.nan
        else:
            self.mean_ret = float(s.mean())
            self.std_ret = float(s.std(ddof=1))

    def mean(self) -> float: return self.mean_ret
    def std(self)  -> float: return self.std_ret
    def tail(self, n: int = 5) -> pd.Series: return self.data.tail(n)


@dataclass
class VolumeActivitySeries:
    """
    Z-score de actividad de volumen (volumen anómalo).
    z = (volume - media_20) / std_20
    """
    symbol: str
    source: str
    data: pd.Series            # z-score
    mean_val: float = field(init=False)
    std_val: float = field(init=False)

    def __post_init__(self):
        s = pd.to_numeric(self.data, errors="coerce")
        self.mean_val = float(s.mean()) if not s.empty else np.nan
        self.std_val  = float(s.std(ddof=1)) if not s.empty else np.nan

    def mean(self) -> float: return self.mean_val
    def std(self)  -> float: return self.std_val
    def tail(self, n: int = 5) -> pd.Series: return self.data.tail(n)


@dataclass
class VolatilitySeries:
    """
    Volatilidad móvil anualizada (p.ej., std de retornos 20d * sqrt(252)).
    """
    symbol: str
    source: str
    data: pd.Series            # volatilidad anualizada
    mean_vol: float = field(init=False)

    def __post_init__(self):
        s = pd.to_numeric(self.data, errors="coerce")
        self.mean_vol = float(s.mean()) if not s.empty else np.nan

    def tail(self, n: int = 5) -> pd.Series: return self.data.tail(n)