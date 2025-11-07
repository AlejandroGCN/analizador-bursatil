from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
import pandas as pd

from data_extractor.core.base.base_series import (
    validate_datetime_index,
    mean_std_from_series,
    SeriesDataAccess,
)


@dataclass
class PerformanceSeries(SeriesDataAccess):
    """
    Serie 1D de rendimientos (pct o log) derivados del 'close'.
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
        return self.mean_ret

    def std(self) -> float:
        return self.std_ret
