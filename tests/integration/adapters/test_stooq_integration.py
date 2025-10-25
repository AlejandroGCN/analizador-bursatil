import pytest
import pandas as pd

# Verificar si pandas_datareader está disponible
try:
    from data_extractor.adapters.stooq_adapter import StooqAdapter, _PDR_OK
    STOOQ_INTEGRATION_AVAILABLE = _PDR_OK
except ImportError:
    STOOQ_INTEGRATION_AVAILABLE = False

@pytest.mark.integration
@pytest.mark.skipif(not STOOQ_INTEGRATION_AVAILABLE, reason="pandas_datareader no disponible en Python 3.12+")
def test_stooq_request_api(recent_window_days, skip_if_offline):
    start, end = recent_window_days
    s = StooqAdapter(timeout=20)
    df = s.download_symbol("AAPL", start=start, end=end, interval="1d")
    assert not df.empty, "El DataFrame devuelto está vacío"
    assert {"Open","High","Low","Close","Adj Close","Volume"} <= set(df.columns)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.is_monotonic_increasing

    print(f"\n📈 Stooq devolvió {len(df)} filas desde {df.index.min()} hasta {df.index.max()}")
    print(df.head(3))
