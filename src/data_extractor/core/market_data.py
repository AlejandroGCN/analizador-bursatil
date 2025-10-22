# core/market_data.py
from enum import Enum

class DataKind(str, Enum):
    OHLCV = "ohlcv"
    RETURNS_PCT = "returns_pct"
    RETURNS_LOG = "returns_log"
    VOLUME_ACTIVITY = "volume_activity"
    VOLATILITY = "volatility"
