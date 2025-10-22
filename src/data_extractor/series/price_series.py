from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd

from data_extractor.core.base.base_series import validate_datetime_index, mean_std_from_series, _FrameLikeMixin


@dataclass
class PriceSeries(_FrameLikeMixin):
    """
    Serie temporal de precios **OHLCV** ya normalizada.
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
        """Desv. típica del precio de cierre."""
        return self.std_close

    def describe(self) -> pd.DataFrame:
        """Resumen estadístico de las columnas OHLCV."""
        return self.data.describe()
