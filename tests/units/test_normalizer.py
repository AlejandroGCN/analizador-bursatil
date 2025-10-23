# tests/units/test_normalizer.py
import pandas as pd
import numpy as np
import pytest

from data_extractor.core.normalizer import normalizer_tipology
from data_extractor.series import (
    PriceSeries,
    PerformanceSeries,
    VolumeActivitySeries,
    VolatilitySeries,
)

# ---------------------------------------
# Helpers
# ---------------------------------------
def _make_ohlcv_df(n=40):
    idx = pd.date_range("2025-01-01", periods=n, freq="D")
    base = np.linspace(100, 120, n)
    # Nota: los nombres aquí dan igual; el normalizador renombra y escoge columnas
    # pero incluimos todas para cubrir caminos (Adj Close/Close)
    return pd.DataFrame(
        {
            "Open": base + np.random.normal(0, 0.5, n),
            "High": base + 1.0 + np.random.normal(0, 0.5, n),
            "Low": base - 1.0 + np.random.normal(0, 0.5, n),
            "Close": base + np.random.normal(0, 0.5, n),
            "Adj Close": base + np.random.normal(0, 0.5, n),
            "Volume": np.random.randint(1_000, 10_000, n),
        },
        index=idx,
    )

def _make_ohlcv_partial(start, periods, freq="D", with_nans=False):
    idx = pd.date_range(start, periods=periods, freq=freq)
    base = np.linspace(100, 110, periods)
    df = pd.DataFrame(
        {
            "Open": base + np.random.normal(0, 0.2, periods),
            "High": base + 1.0 + np.random.normal(0, 0.2, periods),
            "Low": base - 1.0 + np.random.normal(0, 0.2, periods),
            "Close": base + np.random.normal(0, 0.2, periods),
            "Adj Close": base + np.random.normal(0, 0.2, periods),
            "Volume": np.random.randint(1_000, 5_000, periods),
        },
        index=idx,
    )
    if with_nans and len(df) >= 3:
        df.loc[idx[1], ["Open", "High", "Low", "Close", "Adj Close"]] = np.nan
        df.loc[idx[-2], ["Close", "Adj Close"]] = np.nan
    return df

# ---------------------------------------
# Test principal: todas las tipologías
# ---------------------------------------
@pytest.mark.parametrize(
    "kind,expected_type,extra_kwargs,expect_kind_attr",
    [
        ("ohlcv",          PriceSeries,          {},                        None),
        ("returns_pct",    PerformanceSeries,    {},                        "returns_pct"),
        ("returns_log",    PerformanceSeries,    {},                        "returns_log"),
        ("volume_activity",VolumeActivitySeries, {"window": 5},             None),
        ("volatility",     VolatilitySeries,     {"window": 5, "ann_factor": 252}, None),
    ],
)
def test_normalizer_all_tipologies(kind, expected_type, extra_kwargs, expect_kind_attr):
    raw_frames = {"BTCUSDT": _make_ohlcv_df(n=40)}

    out = normalizer_tipology(
        raw_frames,
        kind=kind,
        source_name="test_source",
        align="union",
        ffill=False,
        bfill=False,
        **extra_kwargs
    )

    assert isinstance(out, dict) and "BTCUSDT" in out
    obj = out["BTCUSDT"]

    # Tipo correcto
    assert isinstance(obj, expected_type)

    # Metadatos
    assert getattr(obj, "symbol", None) == "BTCUSDT"
    assert getattr(obj, "source", None) == "test_source"

    # Datos no vacíos
    assert len(getattr(obj, "data")) > 0

    # Estructura de data según la tipología
    if kind == "ohlcv":
        # PriceSeries.data debe ser DataFrame con columnas minúsculas
        assert isinstance(obj.data, pd.DataFrame)
        cols = ["open", "high", "low", "close", "volume"]
        for c in cols:
            assert c in obj.data.columns, f"Falta columna '{c}' en OHLCV normalizado"
    else:
        # El resto deben ser Series 1D numéricas
        assert isinstance(obj.data, pd.Series)
        # Al menos que sean convertibles a numérico y sin todo NaN
        s = pd.to_numeric(obj.data, errors="coerce")
        assert s.notna().any(), f"{kind} no debería ser todo NaN"

        # Para PerformanceSeries validamos el atributo kind específico
        if expect_kind_attr is not None:
            assert getattr(obj, "kind", None) == expect_kind_attr

# ---------------------------------------
# Alineación intersect + ffill/bfill
# ---------------------------------------
def test_ffill_bfill_for_ohlcv():
    # A: 2025-01-01 .. 2025-01-10
    df_a = _make_ohlcv_partial("2025-01-01", periods=10, with_nans=False)
    # B: 2025-01-05 .. 2025-01-14, con NaNs internos
    df_b = _make_ohlcv_partial("2025-01-05", periods=10, with_nans=True)

    raw = {"BTCUSDT": df_a, "ETHUSDT": df_b}

    out = normalizer_tipology(
        raw_frames=raw,
        kind="ohlcv",
        source_name="test_source",
        align="intersect",
        ffill=True,
        bfill=True,
    )

    assert set(out.keys()) == {"BTCUSDT", "ETHUSDT"}

    a_obj = out["BTCUSDT"]
    b_obj = out["ETHUSDT"]

    assert isinstance(a_obj, PriceSeries)
    assert isinstance(b_obj, PriceSeries)

    assert a_obj.symbol == "BTCUSDT" and a_obj.source == "test_source"
    assert b_obj.symbol == "ETHUSDT" and b_obj.source == "test_source"

    expected_index = df_a.index.intersection(df_b.index)
    assert len(expected_index) > 0
    pd.testing.assert_index_equal(a_obj.data.index, expected_index)
    pd.testing.assert_index_equal(b_obj.data.index, expected_index)

    # Columnas en minúsculas (salida normalizada)
    cols = ["open", "high", "low", "close", "volume"]
    for c in cols:
        assert c in a_obj.data.columns
        assert c in b_obj.data.columns

    # Sin NaNs tras ffill/bfill en el rango común
    assert not a_obj.data[cols].isna().any().any()
    assert not b_obj.data[cols].isna().any().any()
