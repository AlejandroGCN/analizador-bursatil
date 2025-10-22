from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd

from ..core.base_series import validate_datetime_index, mean_std_from_series, _SeriesLikeMixin


@dataclass
class VolumeActivitySeries(_SeriesLikeMixin):
    """
    Z-score de actividad de volumen (volumen anómalo).
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
        return self.mean_val

    def std(self) -> float:
        return self.std_val
