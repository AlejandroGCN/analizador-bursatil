from __future__ import annotations

from typing import Tuple
import pandas as pd
import numpy as np

__all__ = [
    "validate_datetime_index",
    "mean_std_from_series",
    "_SeriesLikeMixin",
    "_FrameLikeMixin",
]


# ──────────────────────────────────────────────────────────────────────────────
# Validaciones y utilidades comunes
# ──────────────────────────────────────────────────────────────────────────────

def validate_datetime_index(idx: pd.Index) -> None:
    """
    Valida que el índice sea un DatetimeIndex monótono ascendente y sin duplicados.
    Lanza TypeError/ValueError si no cumple.
    """
    if not isinstance(idx, pd.DatetimeIndex):
        raise TypeError("El índice debe ser pd.DatetimeIndex.")
    if not idx.is_monotonic_increasing:
        raise ValueError("El índice temporal debe estar ordenado ascendentemente.")
    if idx.has_duplicates:
        raise ValueError("El índice temporal no debe tener duplicados.")


def mean_std_from_series(s: pd.Series) -> Tuple[float, float]:
    """
    Calcula (mean, std) numéricos con ddof=1 si hay ≥2 valores no-NaN.
    Devuelve (NaN, NaN) si no hay datos suficientes.
    """
    s = pd.to_numeric(s, errors="coerce")
    n = s.dropna().shape[0]
    mean = float(s.mean()) if n >= 1 else float("nan")
    std = float(s.std(ddof=1)) if n >= 2 else float("nan")
    return mean, std


# ──────────────────────────────────────────────────────────────────────────────
# Mixins para evitar repetición en las dataclasses de series
# ──────────────────────────────────────────────────────────────────────────────

class _SeriesLikeMixin:
    """
    Mixin para clases con atributo `data: pd.Series`.
    Proporciona: __len__, empty, index, to_series, tail.
    """
    data: pd.Series  # lo define la subclase

    def __len__(self) -> int:
        return len(self.data)

    @property
    def empty(self) -> bool:
        return self.data.empty

    @property
    def index(self) -> pd.DatetimeIndex:
        # ayuda al IDE; el índice es un DatetimeIndex tras el normalizador
        return self.data.index  # type: ignore[return-value]

    def to_series(self) -> pd.Series:
        return self.data.copy()

    def tail(self, n: int = 5) -> pd.Series:
        return self.data.tail(n)


class _FrameLikeMixin:
    """
    Mixin para clases con atributo `data: pd.DataFrame`.
    Proporciona: __len__, empty, index, to_frame, tail.
    """
    data: pd.DataFrame  # lo define la subclase

    def __len__(self) -> int:
        return len(self.data)

    @property
    def empty(self) -> bool:
        return self.data.empty

    @property
    def index(self) -> pd.DatetimeIndex:
        return self.data.index  # type: ignore[return-value]

    def to_frame(self) -> pd.DataFrame:
        return self.data.copy()

    def tail(self, n: int = 5) -> pd.DataFrame:
        return self.data.tail(n)
