from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd

from ..core.base_series import validate_datetime_index, _SeriesLikeMixin


@dataclass
class VolatilitySeries(_SeriesLikeMixin):
    """
    Volatilidad móvil **anualizada** (p.ej., std de retornos 20d * sqrt(252)).
    """
    symbol: str
    source: str
    data: pd.Series
    mean_vol: float = field(init=False)

    def __post_init__(self) -> None:
        validate_datetime_index(self.data.index)
        s = pd.to_numeric(self.data, errors="coerce")
        self.mean_vol = float(s.dropna().mean()) if s.notna().any() else float("nan")
