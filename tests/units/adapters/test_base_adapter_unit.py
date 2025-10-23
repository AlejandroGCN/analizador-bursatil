import pandas as pd
import pytest
from data_extractor.core.base.base_adapter import BaseAdapter
from data_extractor.core.errors import ExtractionError, SymbolNotFound

# Simula un adaptador que siempre devuelve datos válidos
class DummyAdapterOK(BaseAdapter):
    name = "dummy_ok"
    def download_symbol(self, symbol, start, end, interval, **opts):
        idx = pd.to_datetime(["2024-01-01 00:00:00", "2024-01-01 01:00:00"])
        return pd.DataFrame({
            "Open": [1, 2], "High": [2, 3], "Low": [0.5, 1.5], "Close": [1.5, 2.5],
            "Adj Close": [1.5, 2.5], "Volume": [10, 20]
        }, index=idx)

# Simula un adaptador que siempre falla
class DummyAdapterFail(BaseAdapter):
    name = "dummy_fail"
    def download_symbol(self, symbol, start, end, interval, **opts):
        raise SymbolNotFound("no data", source=self.name, symbol=symbol)

# Test 1: Verifica que se lanza un error si no se pasa ningún símbolo
def test_error_if_no_symbols_provided():
    adapter = DummyAdapterOK()
    with pytest.raises(ExtractionError):
        adapter.get_symbols(None, start=None, end=None, interval="1h")

# Test 2: Verifica que se devuelve un DataFrame válido para un solo símbolo
def test_single_symbol_returns_valid_dataframe():
    adapter = DummyAdapterOK()
    result = adapter.get_symbols("AAPL", start=None, end=None, interval="1h")
    assert set(result.keys()) == {"AAPL"}
    df = result["AAPL"]
    assert {"Open", "High", "Low", "Close", "Adj Close", "Volume"} <= set(df.columns)
    assert len(df) == 2
    assert df.index.is_monotonic_increasing

# Test 3: Verifica que se manejan errores en paralelo y se devuelven los símbolos válidos
def test_parallel_download_handles_mixed_success_and_failure():
    class MixedAdapter(BaseAdapter):
        name = "mixed"
        def download_symbol(self, symbol, start, end, interval, **opts):
            if symbol == "FAIL":
                raise SymbolNotFound("no data", source=self.name, symbol=symbol)
            return DummyAdapterOK().download_symbol(symbol, start, end, interval)

    adapter = MixedAdapter(max_workers=3)
    result = adapter.get_symbols(["AAA", "BBB", "FAIL"], start=None, end=None, interval="1h")
    assert set(result.keys()) == {"AAA", "BBB"}
    assert all(df.index.is_monotonic_increasing for df in result.values())
