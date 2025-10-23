import pytest
import pandas as pd
from data_extractor.adapters.binance_adapter import BinanceAdapter

@pytest.mark.integration
def test_binance_real_request_api(recent_window_days, skip_if_offline):
    start, end = recent_window_days
    b = BinanceAdapter(timeout=15)
    df = b.download_symbol("BTCUSDT", start=start, end=end, interval="1h")
    assert not df.empty
    assert {"Open","High","Low","Close","Adj Close","Volume"} <= set(df.columns)
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert df.index.is_monotonic_increasing
