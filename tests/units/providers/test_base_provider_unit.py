# tests/units/providers/test_base_provider_unit.py
import importlib.util
import pytest
import pandas as pd

from data_extractor.core.base.base_provider import BaseProvider
from data_extractor.adapters.yahoo_adapter import YahooAdapter
from data_extractor.adapters.binance_adapter import BinanceAdapter

has_yf = importlib.util.find_spec("yfinance") is not None

def _best_close(df: pd.DataFrame):
    return df["Adj Close"] if "Adj Close" in df.columns else df["Close"]

def _get_close(series_df: pd.DataFrame) -> pd.Series:
    # Devuelve la columna 'close' de forma case-insensitive
    for c in series_df.columns:
        if c.lower() == "close":
            return series_df[c]
    raise AssertionError("La serie del provider no tiene columna 'close'")

@pytest.mark.integration
def test_provider_end_to_end_pipeline():
    # =========================
    # 1) YAHOO (1 símbolo, 1d)
    # =========================
    if not has_yf:
        pytest.skip("yfinance no instalado: salto sección Yahoo")

    start_y = pd.Timestamp("2024-01-02")
    end_y   = pd.Timestamp("2024-01-10")

    # baseline adapter (OHLCV normalizado por BaseAdapter)
    ya = YahooAdapter(timeout=20, max_workers=1)
    base_yahoo = ya.get_symbols(["AAPL"], start_y, end_y, "1d")["AAPL"]

    # provider con el mismo adapter
    yp = BaseProvider(source_name="yahoo", adapter=ya)
    out_yahoo = yp.get_symbols(["AAPL"], start_y, end_y, "1d", align="union")
    ps_yahoo = out_yahoo["AAPL"]
    dfp_yahoo = ps_yahoo.data  # <-- usar .data

    assert not dfp_yahoo.empty
    assert isinstance(dfp_yahoo.index, pd.DatetimeIndex)
    assert dfp_yahoo.index.is_monotonic_increasing

    # índice y longitudes coherentes
    assert len(dfp_yahoo) == len(base_yahoo)
    assert dfp_yahoo.index.min() >= base_yahoo.index.min()
    assert dfp_yahoo.index.max() <= base_yahoo.index.max()

    # comparar el 'close' del provider con el mejor close del adapter
    close_provider = _get_close(dfp_yahoo).astype(float)
    close_target   = _best_close(base_yahoo).reindex(dfp_yahoo.index).astype(float)

    pd.testing.assert_series_equal(
        close_provider.round(8),
        close_target.round(8),
        check_names=False
    )

    # ==========================================
    # 2) YAHOO (2 símbolos) — union vs intersect
    # ==========================================
    syms = ["AAPL", "MSFT"]
    out_union = yp.get_symbols(syms, start_y, end_y + pd.Timedelta(days=10), "1d", align="union")
    out_inter = yp.get_symbols(syms, start_y, end_y + pd.Timedelta(days=10), "1d", align="intersection")

    assert set(out_union.keys()) == set(syms)
    assert set(out_inter.keys()) == set(syms)

    for s in syms:
        df_u = out_union[s].data
        df_i = out_inter[s].data
        assert isinstance(df_u.index, pd.DatetimeIndex) and df_u.index.is_monotonic_increasing
        assert isinstance(df_i.index, pd.DatetimeIndex) and df_i.index.is_monotonic_increasing
        assert len(df_u) >= len(df_i)  # union nunca más corto que intersection

    inter_idx = out_inter[syms[0]].data.index
    for s in syms[1:]:
        pd.testing.assert_index_equal(inter_idx, out_inter[s].data.index)

    # ==========================
    # 3) BINANCE (BTCUSDT, 1h) - SKIP por restricciones geográficas
    # ==========================
    pytest.skip("Binance API restringida geográficamente en GitHub Actions")

    bp = BaseProvider(source_name="binance", adapter=ba)
    out_binance = bp.get_symbols(["BTCUSDT"], start_b, end_b, "1h", align="union")
    ps_binance = out_binance["BTCUSDT"]
    dfp_binance = ps_binance.data  # <-- usar .data

    assert not dfp_binance.empty
    assert isinstance(dfp_binance.index, pd.DatetimeIndex)
    assert dfp_binance.index.is_monotonic_increasing
    assert len(dfp_binance) == len(base_binance)
    assert dfp_binance.index.min() >= base_binance.index.min()
    assert dfp_binance.index.max() <= base_binance.index.max()

    close_provider_b = _get_close(dfp_binance).astype(float)
    close_target_b   = _best_close(base_binance).reindex(dfp_binance.index).astype(float)

    pd.testing.assert_series_equal(
        close_provider_b.round(8),
        close_target_b.round(8),
        check_names=False
    )
