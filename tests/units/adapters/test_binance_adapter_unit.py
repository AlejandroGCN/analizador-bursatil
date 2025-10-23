import pandas as pd
import pytest
from data_extractor.adapters.binance_adapter import BinanceAdapter
from data_extractor.core.errors import SymbolNotFound
from utils_http import DummyResp

def _make_klines(n=3):
    """
    Devuelve una lista de klines estilo Binance:
    [openTime, open, high, low, close, volume, closeTime, ...]
    """
    base = pd.Timestamp("2025-01-01 00:00:00")
    out = []
    for i in range(n):
        t = int((base + pd.Timedelta(hours=i)).timestamp() * 1000)
        out.append([t, "10.0", "11.0", "9.0", "10.5", "100.0", t+3600000, 0, 0, 0, 0, 0])
    return out

class FakeSession:
    def __init__(self, resp):
        self._resp = resp
    def get(self, *args, **kwargs):
        return self._resp

def test_parses_valid_klines_into_dataframe():
    klines = _make_klines(n=3)
    session = FakeSession(DummyResp(status_code=200, json_data=klines))
    adapter = BinanceAdapter(timeout=5, session=session)
    df = adapter.download_symbol("BTCUSDT", start=None, end=None, interval="1h", limit=3)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Open","High","Low","Close","Adj Close","Volume"]
    assert len(df) == 3
    assert df.index.is_monotonic_increasing

def test_invalid_symbol_raises_symbolnotfound():
    payload = {"code": -1121, "msg": "Invalid symbol."}
    session = FakeSession(DummyResp(status_code=400, json_data=payload, text="Invalid symbol"))
    adapter = BinanceAdapter(timeout=5, session=session)
    with pytest.raises(SymbolNotFound):
        adapter.download_symbol("BADPAIR", start=None, end=None, interval="1h")
