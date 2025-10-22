from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
import pandas as pd

from .base_series import (
    validate_datetime_index,
    mean_std_from_series,
    _SeriesLikeMixin,
    _FrameLikeMixin,
)

__all__ = [
    "PriceSeries",
    "PerformanceSeries",
    "VolumeActivitySeries",
    "VolatilitySeries",
]


# Invariantes esperadas desde el normalizador:
#  - Index: pd.DatetimeIndex (tz-naive o tz-aware consistente)
#  - Index: monótono ascendente y sin duplicados
#  - Columnas numéricas o convertibles (no numéricos -> NaN)


@dataclass
class PriceSeries(_FrameLikeMixin):
    """
    Serie temporal de precios **OHLCV** ya normalizada.

    Requisitos:
      - `data.index` es `pd.DatetimeIndex`, monótono y sin duplicados.
      - Columnas mínimas: {'open','high','low','close','volume'} (casing libre).
      - Columnas numéricas o convertibles (no numéricos -> NaN).

    Atributos:
      symbol, source, data
      mean_close/std_close: estadísticos del cierre.
    """
    symbol: str
    source: str
    data: pd.DataFrame
    mean_close: float = field(init=False)
    std_close: float = field(init=False)

    def __post_init__(self) -> None:
        validate_datetime_index(self.data.index)

        required = {"open", "high", "low", "close", "volume"}
        cols_lower = {c.lower() for c in self.data.columns}
        missing = required - cols_lower
        if missing:
            raise ValueError(f"Faltan columnas OHLCV requeridas: {sorted(missing)}")

        # Asegurar numérico respetando el casing real
        for req in required:
            col = next((c for c in self.data.columns if c.lower() == req), None)
            if col is not None:
                self.data[col] = pd.to_numeric(self.data[col], errors="coerce")

        if len(self.data) == 0:
            self.mean_close = float("nan")
            self.std_close = float("nan")
            return

        close_col = next((c for c in self.data.columns if c.lower() == "close"), None)
        close = self.data[close_col] if close_col else pd.Series(dtype=float)
        self.mean_close, self.std_close = mean_std_from_series(close)

    def mean(self) -> float:
        """Media del precio de cierre."""
        return self.mean_close

    def std(self) -> float:
        """Desv. típica del precio de cierre (ddof=1 si hay ≥2 puntos)."""
        return self.std_close

    def describe(self) -> pd.DataFrame:
        """Resumen estadístico de las columnas OHLCV."""
        return self.data.describe()


@dataclass
class PerformanceSeries(_SeriesLikeMixin):
    """
    Serie 1D de rendimientos (pct o log) derivados del 'close'.

    Requisitos:
      - `data.index` es `pd.DatetimeIndex` monótono y sin duplicados.
      - `data` es una Serie 1D numérica.
      - kind ∈ {'returns_pct','returns_log'}.

    Atributos:
      mean_ret/std_ret: estadísticos de la serie.
    """
    symbol: str
    source: str
    data: pd.Series
    kind: Literal["returns_pct", "returns_log"]
    mean_ret: float = field(init=False)
    std_ret: float = field(init=False)

    def __post_init__(self) -> None:
        validate_datetime_index(self.data.index)
        self.mean_ret, self.std_ret = mean_std_from_series(self.data)

    def mean(self) -> float:
        """Media de retornos."""
        return self.mean_ret

    def std(self) -> float:
        """Desv. típica de retornos (ddof=1 si ≥2)."""
        return self.std_ret


@dataclass
class VolumeActivitySeries(_SeriesLikeMixin):
    """
    Z-score de actividad de volumen (volumen anómalo).
    Fórmula típica: z = (volume - media_20) / std_20

    Requisitos:
      - `data` es `pd.Series` con z-scores alineados temporalmente.
    """
    symbol: str
    source: str
    data: pd.Series
    mean_val: float = field(init=False)
    std_val: float = field(init=False)

    def __post_init__(self) -> None:
        validate_datetime_index(self.data.index)
        self.mean_val, self.std_val = mean_std_from_series(self.data)

    def mean(self) -> float:
        """Media del z-score."""
        return self.mean_val

    def std(self) -> float:
        """Desv. típica del z-score (ddof=1 si ≥2)."""
        return self.std_val


@dataclass
class VolatilitySeries(_SeriesLikeMixin):
    """
    Volatilidad móvil **anualizada** (p.ej., std de retornos 20d * sqrt(252)).

    Requisitos:
      - `data` es `pd.Series` con la volatilidad anualizada por fecha.
      - La ventana y factor de anualización las define el normalizador.
    """
    symbol: str
    source: str
    data: pd.Series
    mean_vol: float = field(init=False)

    def __post_init__(self) -> None:
        validate_datetime_index(self.data.index)
        s = pd.to_numeric(self.data, errors="coerce")
        self.mean_vol = float(s.dropna().mean()) if s.notna().any() else float("nan")
