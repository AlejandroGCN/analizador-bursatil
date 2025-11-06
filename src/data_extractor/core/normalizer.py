import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Callable

from data_extractor.core.errors import NormalizationError
from data_extractor.series import (
    PriceSeries,
    PerformanceSeries,
    VolumeActivitySeries,
    VolatilitySeries,
)

logger = logging.getLogger(__name__)

# Constantes para nombres de columnas
ADJ_CLOSE_COL = "Adj Close"
OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]

# Utilidad para extraer columnas con tolerancia a nombres alternativos
def _safe_col(df: pd.DataFrame, names: str | list[str], idx: pd.Index) -> pd.Series:
    if isinstance(names, str):
        names = [names]
    col_map = {col.lower(): col for col in df.columns}
    for name in names:
        col = col_map.get(name.lower())
        if col:
            return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(np.nan, index=idx, dtype=float)

# Normaliza un DataFrame a formato OHLCV estándar
def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=OHLCV_COLUMNS, dtype=float)

    # Determinar si necesitamos copiar y modificar el DataFrame
    needs_copy = (
        not isinstance(df.index, pd.DatetimeIndex) or 
        df.index.tz is not None or 
        df.index.has_duplicates
    )
    
    if needs_copy:
        df = df.copy()
        try:
            df.index = pd.to_datetime(df.index)
        except Exception as e:
            raise NormalizationError(f"Índice no convertible a fecha: {e}")
        
        if getattr(df.index, "tz", None):
            df.index = df.index.tz_localize(None)
        df = df[~df.index.duplicated(keep="last")]
    
    idx = df.index.sort_values() if needs_copy else df.index

    return pd.DataFrame({
        "open": _safe_col(df, "Open", idx),
        "high": _safe_col(df, "High", idx),
        "low": _safe_col(df, "Low", idx),
        "close": _safe_col(df, [ADJ_CLOSE_COL, "Close"], idx),
        "volume": _safe_col(df, "Volume", idx),
    }, index=idx)

# Alinea múltiples DataFrames por índice (union o intersect)
def _align_dict(dfs: Dict[str, pd.DataFrame], align: str = "union") -> Dict[str, pd.DataFrame]:
    if not dfs:
        return {}

    if align == "intersect":
        idx = None
        for df in dfs.values():
            idx = df.index if idx is None else idx.intersection(df.index)
    else:
        idx = pd.Index([])
        for df in dfs.values():
            idx = idx.union(df.index)

    idx = pd.DatetimeIndex(idx).sort_values()
    return {key: df.reindex(idx) for key, df in dfs.items()}

# Rellena NaNs con ffill y/o bfill
def _apply_fill(df: pd.DataFrame, ffill: bool, bfill: bool) -> pd.DataFrame:
    if not ffill and not bfill:
        return df
    
    df = df.copy(deep=False)
    if ffill and bfill:
        return df.ffill().bfill()
    if ffill:
        return df.ffill()
    # At this point, bfill must be True (since if not ffill and not bfill, we returned earlier)
    return df.bfill()

# Constructores de series normalizadas
def _build_ohlcv(symbol: str, source: str, df: pd.DataFrame, **_: Any) -> PriceSeries:
    return PriceSeries(symbol, source, df[OHLCV_COLUMNS])

def _build_returns_pct(symbol: str, source: str, df: pd.DataFrame, **_: Any) -> PerformanceSeries:
    returns = df["close"].pct_change().dropna()
    return PerformanceSeries(symbol, source, returns, kind="returns_pct")

def _build_returns_log(symbol: str, source: str, df: pd.DataFrame, **_: Any) -> PerformanceSeries:
    log_returns = np.log(df["close"] / df["close"].shift(1)).dropna()
    return PerformanceSeries(symbol, source, log_returns, kind="returns_log")

def _build_volume_activity(symbol: str, source: str, df: pd.DataFrame, *, window: int = 20, **_: Any) -> VolumeActivitySeries:
    volume = df["volume"].astype(float)
    mean = volume.rolling(window, min_periods=window).mean()
    std = volume.rolling(window, min_periods=window).std(ddof=1).replace(0, np.nan)
    zscore = (volume - mean) / std
    return VolumeActivitySeries(symbol, source, zscore)

def _build_volatility(symbol: str, source: str, df: pd.DataFrame, *, window: int = 20, ann_factor: int = 252, **_: Any) -> VolatilitySeries:
    log_ret = np.log(df["close"] / df["close"].shift(1))
    vol = log_ret.rolling(window, min_periods=window).std(ddof=1) * np.sqrt(ann_factor)
    return VolatilitySeries(symbol, source, vol)

# Mapeo de tipos de normalización a sus constructores
NORMALIZERS: Dict[str, Callable[..., Any]] = {
    "ohlcv": _build_ohlcv,
    "returns_pct": _build_returns_pct,
    "returns_log": _build_returns_log,
    "volume_activity": _build_volume_activity,
    "volatility": _build_volatility,
}

# Pipeline principal de normalización
def normalizer_tipology(
        raw_frames: Dict[str, pd.DataFrame],
        *,
        kind: str,
        source_name: str,
        align: str = "union",
        ffill: bool = False,
        bfill: bool = False,
        **params: Any,
) -> Dict[str, Any]:
    """
    Pipeline de normalización:
    1. Convierte cada DataFrame a formato OHLCV.
    2. Alinea índices (union o intersect).
    3. Aplica relleno si se solicita.
    4. Construye objetos tipológicos según `kind`.
    """
    normalized = {sym: normalize_ohlcv(df) for sym, df in raw_frames.items()}
    aligned = _align_dict(normalized, align)
    filled = {sym: _apply_fill(df, ffill, bfill) for sym, df in aligned.items()} if (ffill or bfill) else aligned

    kind_key = kind.lower()
    builder = NORMALIZERS.get(kind_key)
    if builder is None:
        raise NormalizationError(f"Tipo de normalización desconocido: {kind}")

    result: Dict[str, Any] = {}
    for sym, df in filled.items():
        try:
            result[sym] = builder(sym, source_name, df, **params)
        except TypeError:
            result[sym] = builder(sym, source_name, df)
    return result
