import os
import pytest
import pandas as pd
from data_extractor.adapters.tiingo_adapter import TiingoAdapter
from data_extractor.core.errors import ExtractionError

# Verificar si hay API key disponible
has_tiingo_key = os.environ.get("TIINGO_API_KEY") is not None

REQUIRED_COLS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]


@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_aapl_daily_small_window(skip_if_offline):
    """
    Test de integración: descarga real de AAPL desde Tiingo API.
    
    Requiere:
    - Conexión a Internet
    - Variable de entorno TIINGO_API_KEY configurada
    """
    adapter = TiingoAdapter(timeout=20, max_workers=1)
    
    # Ventana de tiempo pequeña para test rápido
    start = pd.Timestamp("2024-01-02")
    end = pd.Timestamp("2024-01-10")
    
    df = adapter.download_symbol("AAPL", start=start, end=end, interval="1d")
    
    # Verificaciones básicas
    assert not df.empty, "Tiingo devolvió un DataFrame vacío en la ventana indicada"
    assert list(df.columns) == REQUIRED_COLS, f"Columnas inesperadas: {list(df.columns)}"
    
    # Verificación de índice
    assert isinstance(df.index, pd.DatetimeIndex), "El índice debe ser DatetimeIndex"
    assert df.index.is_monotonic_increasing, "El índice debe estar en orden ascendente"
    assert df.index.tz is None, "El índice debe quedar tz-naive tras la normalización"
    
    # Verificación de tipos de datos
    for col in REQUIRED_COLS:
        assert pd.api.types.is_numeric_dtype(df[col]), f"La columna {col} debe ser numérica"
    
    # Verificación de rango de fechas
    assert df.index.min() >= start.tz_localize(None)
    assert df.index.max() <= end.tz_localize(None)
    
    # Verificación de valores razonables para AAPL
    assert df["Close"].min() > 0, "Los precios deben ser positivos"
    assert df["Volume"].min() >= 0, "El volumen debe ser no negativo"


@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_multiple_symbols(skip_if_offline):
    """
    Test de integración: descarga múltiples símbolos desde Tiingo.
    """
    adapter = TiingoAdapter(timeout=20, max_workers=2)
    
    symbols = ["AAPL", "MSFT", "GOOGL"]
    start = pd.Timestamp("2024-01-02")
    end = pd.Timestamp("2024-01-05")
    
    results = {}
    for symbol in symbols:
        df = adapter.download_symbol(symbol, start=start, end=end, interval="1d")
        results[symbol] = df
    
    # Verificar que se descargaron todos
    assert len(results) == len(symbols)
    
    # Verificar estructura de cada uno
    for symbol, df in results.items():
        assert not df.empty, f"DataFrame vacío para {symbol}"
        assert list(df.columns) == REQUIRED_COLS
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.is_monotonic_increasing


@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_longer_historical_window(skip_if_offline):
    """
    Test de integración: descarga ventana histórica más larga (1 año).
    """
    adapter = TiingoAdapter(timeout=30, max_workers=1)
    
    # Ventana de 1 año atrás
    end = pd.Timestamp("2024-01-31")
    start = pd.Timestamp("2023-01-01")
    
    df = adapter.download_symbol("AAPL", start=start, end=end, interval="1d")
    
    assert not df.empty
    assert len(df) > 200, "Un año de datos diarios debería tener más de 200 registros"
    assert list(df.columns) == REQUIRED_COLS
    assert df.index.is_monotonic_increasing
    
    # Verificar que no hay gaps extremos (fines de semana son normales)
    date_diffs = df.index.to_series().diff()
    max_gap = date_diffs.max()
    assert max_gap <= pd.Timedelta(days=4), "No debería haber gaps de más de 4 días"


@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_international_symbol(skip_if_offline):
    """
    Test de integración: descarga símbolo internacional desde Tiingo.
    
    Tiingo soporta múltiples exchanges. Probamos un símbolo UK.
    """
    adapter = TiingoAdapter(timeout=20, max_workers=1)
    
    # BP (British Petroleum) en London Stock Exchange
    # Nota: Tiingo puede requerir el sufijo .LON para símbolos UK
    start = pd.Timestamp("2024-01-02")
    end = pd.Timestamp("2024-01-10")
    
    # Intentar con símbolo UK (puede fallar si no está disponible)
    try:
        df = adapter.download_symbol("BP", start=start, end=end, interval="1d")
        
        # Si funciona, verificar estructura
        assert not df.empty
        assert list(df.columns) == REQUIRED_COLS
        assert isinstance(df.index, pd.DatetimeIndex)
        
    except ExtractionError as e:
        # Si el símbolo no está disponible, es esperado
        # Tiingo free tier puede tener cobertura limitada
        pytest.skip(f"Símbolo BP no disponible en Tiingo: {e}")


@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_invalid_symbol_raises_error(skip_if_offline):
    """
    Test de integración: verificar que símbolo inválido lanza error.
    """
    adapter = TiingoAdapter(timeout=20, max_workers=1)
    
    # Símbolo claramente inválido
    with pytest.raises(ExtractionError, match="no encontrado|No se encontraron datos"):
        adapter.download_symbol(
            "INVALID_SYMBOL_12345", 
            start="2024-01-01", 
            end="2024-01-10", 
            interval="1d"
        )


@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_data_quality_checks(skip_if_offline):
    """
    Test de integración: verificar calidad de datos de Tiingo.
    
    Tiingo es conocido por datos de calidad institucional, verificamos:
    - No hay valores NaN en columnas críticas
    - High >= Low
    - Close está entre High y Low
    - Volumen no negativo
    """
    adapter = TiingoAdapter(timeout=20, max_workers=1)
    
    start = pd.Timestamp("2024-01-02")
    end = pd.Timestamp("2024-01-10")
    
    df = adapter.download_symbol("AAPL", start=start, end=end, interval="1d")
    
    # Verificar que no hay NaN en columnas críticas
    critical_cols = ["Open", "High", "Low", "Close"]
    for col in critical_cols:
        assert df[col].notna().all(), f"Columna {col} tiene valores NaN"
    
    # Verificar relaciones lógicas OHLC
    assert (df["High"] >= df["Low"]).all(), "High debe ser >= Low"
    assert (df["Close"] <= df["High"]).all(), "Close debe ser <= High"
    assert (df["Close"] >= df["Low"]).all(), "Close debe ser >= Low"
    assert (df["Open"] <= df["High"]).all(), "Open debe ser <= High"
    assert (df["Open"] >= df["Low"]).all(), "Open debe ser >= Low"
    
    # Verificar volumen
    assert (df["Volume"] >= 0).all(), "Volume debe ser no negativo"
    
    # Verificar que Adj Close existe y es razonable
    assert df["Adj Close"].notna().all(), "Adj Close no debe tener NaN"
    # Adj Close debería estar cerca de Close (sin ajustes recientes)
    price_diff_pct = ((df["Adj Close"] - df["Close"]) / df["Close"] * 100).abs()
    # Permitir hasta 20% de diferencia (por ajustes históricos)
    assert (price_diff_pct <= 20).all(), "Adj Close muy diferente de Close"


@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_date_range_consistency(skip_if_offline):
    """
    Test de integración: verificar que los datos están dentro del rango solicitado.
    """
    adapter = TiingoAdapter(timeout=20, max_workers=1)
    
    start = pd.Timestamp("2024-01-02")
    end = pd.Timestamp("2024-01-10")
    
    df = adapter.download_symbol("AAPL", start=start, end=end, interval="1d")
    
    # Todas las fechas deben estar dentro del rango
    assert (df.index >= start).all(), "Hay fechas anteriores al start"
    assert (df.index <= end).all(), "Hay fechas posteriores al end"
    
    # No debe haber fechas duplicadas
    assert not df.index.has_duplicates, "Hay fechas duplicadas en el índice"


@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")  
def test_tiingo_api_key_from_env(skip_if_offline):
    """
    Test de integración: verificar que el adaptador obtiene API key del entorno.
    """
    # No pasar API key explícitamente, debe obtenerla del entorno
    adapter = TiingoAdapter(timeout=20, max_workers=1)
    
    assert adapter.api_key is not None, "API key debería cargarse del entorno"
    assert len(adapter.api_key) > 10, "API key parece inválida (muy corta)"
    
    # Verificar que funciona haciendo una petición real
    start = pd.Timestamp("2024-01-02")
    end = pd.Timestamp("2024-01-05")
    
    df = adapter.download_symbol("AAPL", start=start, end=end, interval="1d")
    assert not df.empty


@pytest.mark.integration  
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_comparison_with_yahoo(skip_if_offline):
    """
    Test de integración: comparar datos de Tiingo con Yahoo Finance.
    
    Los precios deberían ser muy similares (pueden tener pequeñas diferencias
    por diferentes fuentes de ajuste).
    """
    try:
        from data_extractor.adapters.yahoo_adapter import YahooAdapter
    except ImportError:
        pytest.skip("YahooAdapter no disponible para comparación")
    
    start = pd.Timestamp("2024-01-02")
    end = pd.Timestamp("2024-01-05")
    symbol = "AAPL"
    
    # Descargar desde ambas fuentes
    tiingo_adapter = TiingoAdapter(timeout=20)
    yahoo_adapter = YahooAdapter(timeout=20)
    
    df_tiingo = tiingo_adapter.download_symbol(symbol, start=start, end=end, interval="1d")
    df_yahoo = yahoo_adapter.download_symbol(symbol, start=start, end=end, interval="1d")
    
    # Verificar que ambos tienen datos
    assert not df_tiingo.empty
    assert not df_yahoo.empty
    
    # Alinear por índice (pueden tener días ligeramente diferentes)
    common_dates = df_tiingo.index.intersection(df_yahoo.index)
    
    if len(common_dates) > 0:
        df_tiingo_aligned = df_tiingo.loc[common_dates]
        df_yahoo_aligned = df_yahoo.loc[common_dates]
        
        # Comparar precios de cierre (deberían ser muy similares)
        price_diff_pct = ((df_tiingo_aligned["Close"] - df_yahoo_aligned["Close"]) / 
                         df_yahoo_aligned["Close"] * 100).abs()
        
        # Los precios no deberían diferir más del 1%
        assert (price_diff_pct < 1.0).all(), \
            f"Diferencias significativas entre Tiingo y Yahoo: max {price_diff_pct.max():.2f}%"
    else:
        pytest.skip("No hay fechas comunes entre Tiingo y Yahoo para comparar")


# =============================================================================
# Tests de casos edge que requieren conexión real
# =============================================================================

@pytest.mark.integration
@pytest.mark.skipif(not has_tiingo_key, reason="TIINGO_API_KEY no configurada")
def test_tiingo_recent_data_window(skip_if_offline, recent_window_days):
    """
    Test de integración: descarga datos muy recientes (últimos 3 días).
    """
    start, end = recent_window_days
    
    adapter = TiingoAdapter(timeout=20, max_workers=1)
    
    # Usar símbolo muy líquido para asegurar datos recientes
    df = adapter.download_symbol("SPY", start=start, end=end, interval="1d")
    
    # Puede estar vacío si es fin de semana
    if not df.empty:
        assert list(df.columns) == REQUIRED_COLS
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.is_monotonic_increasing
    else:
        pytest.skip("Sin datos recientes (posiblemente fin de semana)")

