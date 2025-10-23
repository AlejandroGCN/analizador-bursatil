import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]  # carpeta raíz (la que contiene tests/ y src/)
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

import pandas as pd
import pytest

@pytest.fixture
def sample_ohlcv_df():
    idx = pd.to_datetime([
        "2024-01-01 00:00:00",
        "2024-01-01 01:00:00",
        "2024-01-01 02:00:00",
    ])
    df = pd.DataFrame({
        "Open":  [10.0, 11.0, 12.0],
        "High":  [11.0, 12.0, 13.0],
        "Low":   [ 9.0, 10.5, 11.5],
        "Close": [10.5, 11.5, 12.5],
        "Adj Close": [10.5, 11.5, 12.5],
        "Volume": [100, 120, 140],
    }, index=idx)
    return df

@pytest.fixture(autouse=True)
def clear_env_av(monkeypatch):
    # Evita que una API key real influya en los tests
    monkeypatch.delenv("ALPHAVANTAGE_API_KEY", raising=False)

@pytest.fixture
def idx3():
    return pd.date_range("2024-01-01", periods=3, freq="D")