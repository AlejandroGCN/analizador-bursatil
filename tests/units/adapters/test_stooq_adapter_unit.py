import pandas as pd
import pytest

from data_extractor.adapters.stooq_adapter import StooqAdapter
from data_extractor.core.errors import ExtractionError, SymbolNotFound

def test_stooq_ok_builds_dataframe(monkeypatch):
    # Fake de pandas_datareader.data.DataReader
    class FakePDR:
        @staticmethod
        def DataReader(name, data_source, start=None, end=None, interval="d"):
            idx = pd.to_datetime(["2024-01-02", "2024-01-03"])
            # Stooq a veces devuelve columnas en orden distinto; lo simulamos:
            df = pd.DataFrame({
                "Close": [10.5, 11.0],
                "Open":  [10.0, 10.6],
                "High":  [11.0, 11.2],
                "Low":   [ 9.8, 10.2],
                "Volume":[100, 120],
            }, index=idx)
            return df

    monkeypatch.setattr("data_extractor.adapters.stooq_adapter.pdr", FakePDR(), raising=False)
    a = StooqAdapter()
    out = a.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
    assert list(out.columns) == ["Open","High","Low","Close","Adj Close","Volume"]
    assert out.index.is_monotonic_increasing

def test_stooq_invalid_interval_raises():
    a = StooqAdapter()
    with pytest.raises(ExtractionError):
        a.download_symbol("AAPL", start=None, end=None, interval="1h")

def test_stooq_empty_raises(monkeypatch):
    class FakePDR:
        @staticmethod
        def DataReader(name, data_source, start=None, end=None, interval="d"):
            return pd.DataFrame()

    monkeypatch.setattr("data_extractor.adapters.stooq_adapter.pdr", FakePDR(), raising=False)
    a = StooqAdapter()
    with pytest.raises(SymbolNotFound):
        a.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
