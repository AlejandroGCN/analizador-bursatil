# src/ui/input_normalizer.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Callable, Any
import pandas as pd


@dataclass(frozen=True)
class UiQuery:
    """Resultado normalizado y validado de la UI."""
    symbols: List[str]
    start_ts: Optional[pd.Timestamp]
    end_ts: Optional[pd.Timestamp]
    interval_name: str
    kind_str: str


class UiInputNormalizer:
    """
    Normaliza y valida las entradas de la UI para que el extractor
    reciba siempre tipos estables y datos limpios.
    """

    @staticmethod
    def normalize(
            tickers_text: str,
            start_date_sel: Any,     # date | datetime | str | None
            end_date_sel: Any,       # date | datetime | str | None
            interval_sel: str,       # "1d" | "1h" | "1wk" | "1mo"
            kind_label: str,         # etiqueta legible de la UI
            kind_label_to_str: Callable[[str], str],
    ) -> UiQuery:
        # 1) símbolos: split, strip y dedup (conservando orden)
        raw = [t.strip() for t in (tickers_text or "").split(",") if t.strip()]
        symbols = list(dict.fromkeys(raw))

        # 2) fechas a Timestamp
        start_ts = pd.to_datetime(start_date_sel) if start_date_sel else None
        end_ts = pd.to_datetime(end_date_sel) if end_date_sel else None

        # 3) validar rango
        if start_ts and end_ts and start_ts > end_ts:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

        # 4) intervalo (ya validado por el selectbox de UI)
        interval_name = interval_sel

        # 5) tipología estable (string) para el extractor
        kind_str = kind_label_to_str(kind_label)

        return UiQuery(
            symbols=symbols,
            start_ts=start_ts,
            end_ts=end_ts,
            interval_name=interval_name,
            kind_str=kind_str,
        )
