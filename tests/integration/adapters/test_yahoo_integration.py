import importlib.util
import pytest
import pandas as pd
from data_extractor.adapters.yahoo_adapter import YahooAdapter

has_yf = importlib.util.find_spec("yfinance") is not None

REQUIRED_COLS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

@pytest.mark.integration
@pytest.mark.skipif(not has_yf, reason="yfinance no instalado")
def test_yahoo_yfinance_aapl_daily_small_window(skip_if_offline):
    ya = YahooAdapter(timeout=20, max_workers=1)
    start = pd.Timestamp("2024-01-02")
    end = pd.Timestamp("2024-01-10")
    df = ya.download_symbol("AAPL", start=start, end=end, interval="1d")
    assert not df.empty, "Yahoo devolvió un DataFrame vacío en la ventana indicada"
    assert list(df.columns) == REQUIRED_COLS, f"Columnas inesperadas: {list(df.columns)}"
    assert isinstance(df.index, pd.DatetimeIndex), "El índice debe ser DatetimeIndex"
    assert df.index.is_monotonic_increasing, "El índice debe estar en orden ascendente"
    assert df.index.tz is None, "El índice debe quedar tz-naive tras la normalización"
    for c in REQUIRED_COLS:
        assert pd.api.types.is_numeric_dtype(df[c]), f"La columna {c} debe ser numérica"
    assert df.index.min() >= start.tz_localize(None)
    assert df.index.max() <= end.tz_localize(None)
