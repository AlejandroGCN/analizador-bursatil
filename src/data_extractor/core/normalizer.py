from typing import Dict, Optional, Any, Callable
import numpy as np
import pandas as pd
from .base import NormalizationError
from ..models.series import PriceSeries, PerformanceSeries, VolumeActivitySeries, VolatilitySeries

OHLCV = ["open", "high", "low", "close", "volume"]

# ---------------------------
# Normalización base a OHLCV
# ---------------------------
def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve un DataFrame con columnas ['open','high','low','close','volume'] y DateTimeIndex."""
    if df is None or df.empty:
        return pd.DataFrame(columns=OHLCV, dtype=float)

    x = df.copy()

    # Renombrado flexible
    rename_map = {
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Adj Close": "close", "Volume": "volume",
    }
    for col in list(x.columns):
        low = col.lower()
        if low in OHLCV:
            rename_map[col] = low
    x = x.rename(columns=rename_map)

    # Índice a datetime
    if not isinstance(x.index, pd.DatetimeIndex):
        try:
            x.index = pd.to_datetime(x.index)
        except Exception as e:
            raise NormalizationError(f"Índice no convertible a fecha: {e}")

    # Asegura columnas y orden
    for c in OHLCV:
        if c not in x.columns:
            x[c] = pd.Series(dtype=float)
    x = x[OHLCV]

    # Tipos numéricos
    for c in OHLCV:
        x[c] = pd.to_numeric(x[c], errors="coerce")

    return x


def _align_dict(data: Dict[str, pd.DataFrame], how: Optional[str]) -> Dict[str, pd.DataFrame]:
    """
    Alinea todos los DF al mismo índice:
      - 'intersect': intersección
      - 'union': unión
      - None/otro: sin cambios
    """
    if not data or how is None:
        return data

    idxs = [df.index for df in data.values() if not df.empty]
    if not idxs:
        return data

    idx = idxs[0]
    for i in idxs[1:]:
        if how == "intersect":
            idx = idx.intersection(i)
        elif how == "union":
            idx = idx.union(i)
        else:
            return data  # modo desconocido → no tocar

    try:
        idx = idx.sort_values()
    except Exception:
        pass

    return {sym: df.reindex(idx) for sym, df in data.items()}


def _apply_fill(df: pd.DataFrame, ffill: bool, bfill: bool) -> pd.DataFrame:
    """Aplica forward/backward fill sin modificar el original."""
    out = df
    if ffill:
        out = out.ffill()
    if bfill:
        out = out.bfill()
    return out


# -----------------------------------------
# Normalizadores que devuelven OBJETOS
# -----------------------------------------
def normalize_ohlcv_object(symbol: str, source: str, df: pd.DataFrame) -> PriceSeries:
    x = normalize_ohlcv(df)
    return PriceSeries(symbol=symbol, source=source, data=x)


def normalize_returns_pct(symbol: str, source: str, df: pd.DataFrame) -> PerformanceSeries:
    """Rendimiento porcentual: pct_change() sobre 'close'."""
    x = normalize_ohlcv(df)
    s = x["close"].pct_change().dropna()
    return PerformanceSeries(symbol=symbol, source=source, data=s, kind="returns_pct")


def normalize_returns_log(symbol: str, source: str, df: pd.DataFrame) -> PerformanceSeries:
    """Rendimiento logarítmico: log(C_t / C_{t-1})."""
    x = normalize_ohlcv(df)
    s = np.log(x["close"] / x["close"].shift(1)).dropna()
    return PerformanceSeries(symbol=symbol, source=source, data=s, kind="returns_log")


def normalize_volume_activity(
        symbol: str, source: str, df: pd.DataFrame, *, window: int = 20
) -> VolumeActivitySeries:
    """Actividad de volumen como z-score rolling sobre 'volume'."""
    x = normalize_ohlcv(df)
    v = x["volume"]
    z = (v - v.rolling(window).mean()) / v.rolling(window).std(ddof=1)
    return VolumeActivitySeries(symbol=symbol, source=source, data=z)


def normalize_volatility(
        symbol: str, source: str, df: pd.DataFrame, *, window: int = 20, ann_factor: int = 252
) -> VolatilitySeries:
    """Volatilidad anualizada: std rolling de los returns * sqrt(ann_factor)."""
    x = normalize_ohlcv(df)
    r = x["close"].pct_change()
    vol = r.rolling(window).std(ddof=1) * np.sqrt(ann_factor)
    return VolatilitySeries(symbol=symbol, source=source, data=vol)


NORMALIZERS: Dict[str, Callable[..., Any]] = {
    "ohlcv": normalize_ohlcv_object,
    "returns_pct": normalize_returns_pct,
    "returns_log": normalize_returns_log,
    "volume_activity": normalize_volume_activity,
    "volatility": normalize_volatility,
}


def normalizer_tipology(
        raw_frames: Dict[str, pd.DataFrame],
        *,
        kind: str = "ohlcv",
        source_name: str,
        align: Optional[str] = None,
        ffill: bool = False,
        bfill: bool = False,
        **params,
) -> Dict[str, Any]:
    """
    1) Normaliza cada DF a OHLCV
    2) Alinea (union/intersect) si procede
    3) Rellena ffill/bfill si procede
    4) Construye objetos según 'kind'
    """
    # 1) normaliza
    normed = {sym: normalize_ohlcv(df) for sym, df in raw_frames.items()}
    # 2) alinea
    aligned = _align_dict(normed, align)
    # 3) rellena
    filled = {sym: _apply_fill(df, ffill, bfill) for sym, df in aligned.items()} if (ffill or bfill) else aligned
    # 4) construye
    builder = NORMALIZERS.get(kind.lower(), normalize_ohlcv_object)
    built: Dict[str, Any] = {}
    for sym, df in filled.items():
        built[sym] = builder(sym, source_name, df, **params) if params else builder(sym, source_name, df)
    return built
