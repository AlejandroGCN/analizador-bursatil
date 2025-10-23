import pandas as pd
import pytest

from data_extractor.adapters.yahoo_adapter import YahooAdapter
from data_extractor.core.errors import ExtractionError

FAKE_SYMBOL = "AAPL"

def _fake_ohlcv_df():
    idx = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    return pd.DataFrame(
        {
            "Open": [10.0, 11.0, 12.0],
            "High": [12.0, 12.5, 13.0],
            "Low":  [9.0, 10.0, 11.0],
            "Close":[11.0, 11.5, 12.5],
            "Adj Close":[11.0, 11.5, 12.5],
            "Volume":[100, 120, 130],
        },
        index=idx,
    )

# ----------------------------------------------------------------------
# 1) Camino yfinance (incluye prueba intradía, que pdr no soporta)
# ----------------------------------------------------------------------
def test_yahoo_adapter_with_yfinance_backend_for_fake_symbol(monkeypatch):
    ya = YahooAdapter(timeout=5, max_workers=1)

    # Fuerza a usar yfinance y no pdr
    monkeypatch.setattr(ya, "_yf_available", True, raising=False)
    monkeypatch.setattr(ya, "_pdr_available", False, raising=False)

    # Fake de yfinance: Ticker().history(...) -> DataFrame OHLCV
    class FakeTicker:
        def history(self, start=None, end=None, interval=None):
            # Devuelve siempre OHLCV válido
            return _fake_ohlcv_df()

    class FakeYF:
        @staticmethod
        def Ticker(symbol):
            assert symbol == FAKE_SYMBOL
            return FakeTicker()

    monkeypatch.setattr(ya, "yf", FakeYF(), raising=False)

    # 1a) Diario con yfinance
    df_1d = ya.download_symbol(FAKE_SYMBOL, start=None, end=None, interval="1d")
    assert list(df_1d.columns) == ["Open","High","Low","Close","Adj Close","Volume"]
    assert len(df_1d) == 3
    assert df_1d.index.is_monotonic_increasing

    # 1b) Intradía con yfinance (pdr no sirve intradía, pero yfinance sí) :contentReference[oaicite:1]{index=1}
    df_1h = ya.download_symbol(FAKE_SYMBOL, start=None, end=None, interval="1h")
    assert list(df_1h.columns) == ["Open","High","Low","Close","Adj Close","Volume"]
    assert len(df_1h) == 3

# ----------------------------------------------------------------------
# 2) Camino pdr (solo diario). Además, si pedimos intradía sin yf -> error
# ----------------------------------------------------------------------
def test_yahoo_adapter_with_pdr_backend_for_fake_symbol(monkeypatch):
    ya = YahooAdapter(timeout=5, max_workers=1)

    # Fuerza a usar pdr y no yfinance
    monkeypatch.setattr(ya, "_yf_available", False, raising=False)
    monkeypatch.setattr(ya, "_pdr_available", True, raising=False)

    # Fake de pdr: get_data_yahoo(...) -> DataFrame OHLCV
    class FakePDR:
        @staticmethod
        def get_data_yahoo(symbol, start=None, end=None):
            assert symbol == FAKE_SYMBOL
            return _fake_ohlcv_df()

    monkeypatch.setattr(ya, "pdr", FakePDR(), raising=False)

    # 2a) Diario con pdr
    df_1d = ya.download_symbol(FAKE_SYMBOL, start=None, end=None, interval="1d")
    assert list(df_1d.columns) == ["Open","High","Low","Close","Adj Close","Volume"]
    assert len(df_1d) == 3
    assert df_1d.index.is_monotonic_increasing

    # 2b) Intradía con pdr debería fallar (pdr no soporta intradía y el adapter lo bloquea) :contentReference[oaicite:2]{index=2}
    with pytest.raises(ExtractionError):
        ya.download_symbol(FAKE_SYMBOL, start=None, end=None, interval="1h")
