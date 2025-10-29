from __future__ import annotations
import streamlit as st
import pandas as pd
import logging
import traceback
from ui.app_config import build_cfg_and_kind
from ui.services_backend import fetch_market_data
from ui.sidebars import DatosParams
from ui.utils import display_symbol_info, render_symbol_input
from data_extractor.core.errors import ExtractionError, SymbolNotFound

logger = logging.getLogger(__name__)


def _validate_symbol_format(symbol: str) -> bool:
    """Valida el formato de un símbolo individual."""
    if "." in symbol and not any(symbol.endswith(f".{ext}") for ext in ["US", "DE", "FR", "UK", "JP", "CA"]):
        return False
    return True


def _display_date_range_info(df: pd.DataFrame) -> None:
    """Muestra información del rango de fechas de los datos."""
    if not df.empty:
        st.info(f"📅 **Rango de datos:** {df.index.min().strftime('%Y-%m-%d')} a {df.index.max().strftime('%Y-%m-%d')} ({len(df)} registros)")


def _clear_old_cache() -> None:
    """Limpia el cache anterior y resultados de simulaciones antiguos."""
    if "last_data_map" in st.session_state:
        del st.session_state["last_data_map"]
    if "montecarlo_results" in st.session_state:
        del st.session_state["montecarlo_results"]
    if "montecarlo_portfolio" in st.session_state:
        del st.session_state["montecarlo_portfolio"]
    if "reporte_portfolio" in st.session_state:
        del st.session_state["reporte_portfolio"]


def _parse_and_validate_symbols(symbols_text: str) -> list[str]:
    """Parsea y valida los símbolos ingresados."""
    symbols_list = [s.strip() for s in symbols_text.replace(" ", ",").split(",") if s.strip()]
    
    for symbol in symbols_list:
        if not _validate_symbol_format(symbol):
            st.warning(f"⚠️ Advertencia: '{symbol}' parece mal formateado. Verifica que usas comas: 'MSFT, GOOGL'")
    
    if not symbols_list:
        st.error("❌ **Error:** No se pudieron parsear los símbolos. Verifica el formato.")
    
    return symbols_list


def _get_symbol_suggestions(symbol: str, source: str) -> str:
    """
    Proporciona sugerencias cuando un símbolo no se encuentra.
    
    Args:
        symbol: Símbolo que no se encontró
        source: Fuente de datos (yahoo, binance, stooq)
    
    Returns:
        Mensaje con sugerencias
    """
    suggestions = []
    
    if source.lower() == "yahoo":
        suggestions.extend([
            f"Verifica que '{symbol}' es un símbolo válido de Yahoo Finance",
            "Para acciones de EE.UU., usa el símbolo sin sufijo (ej: AAPL, MSFT, GOOGL)",
            "Para acciones internacionales, añade el sufijo del país (ej: SIEMENS.DE, ASML.AS)",
            f"Intenta verificar el símbolo en https://finance.yahoo.com/quote/{symbol}"
        ])
    elif source.lower() == "binance":
        suggestions.extend([
            f"Verifica que '{symbol}' es un par de cripto válido en Binance",
            "Los pares deben estar en formato BASEQUOTE (ej: BTCUSDT, ETHUSDT)",
            "Para stablecoins, usa USDT como quote (ej: BTCUSDT, ETHUSDT)"
        ])
    elif source.lower() == "stooq":
        suggestions.extend([
            f"Verifica que '{symbol}' existe en Stooq",
            "Para acciones de EE.UU., añade .US (ej: AAPL.US, MSFT.US, GOOGL.US)",
            "Otros países: DE (Alemania), FR (Francia), UK (Reino Unido), JP (Japón)"
        ])
    
    return "\n".join(f"- {s}" for s in suggestions)


def _handle_extraction_error(error: Exception, params: DatosParams | None) -> None:
    """
    Maneja errores de extracción con mensajes informativos y sugerencias.
    
    Args:
        error: Excepción capturada
        params: Parámetros de descarga (opcional, para obtener información contextual)
    """
    source_name = params.fuente if params else "la fuente seleccionada"
    
    if isinstance(error, SymbolNotFound):
        symbol = getattr(error, 'symbol', 'símbolo desconocido')
        st.error(f"🚫 **Símbolo no encontrado**: '{symbol}' no existe en {source_name}")
        
        suggestions = _get_symbol_suggestions(symbol, source_name)
        with st.expander("💡 Sugerencias para resolver el problema"):
            st.markdown(suggestions)
            
            st.markdown("**Ejemplos de símbolos válidos por fuente:**")
            if source_name.lower() == "yahoo":
                st.code("AAPL, MSFT, GOOGL, TSLA, AMZN  # Acciones US\nSIEMENS.DE, ASML.AS  # Acciones internacionales")
            elif source_name.lower() == "binance":
                st.code("BTCUSDT, ETHUSDT, BNBBTC  # Pares de criptomonedas")
            else:
                st.code("AAPL.US, MSFT.US, GOOGL.US  # Formato Stooq")
    
    elif isinstance(error, ExtractionError):
        symbol = getattr(error, 'symbol', None)
        error_message = str(error)
        
        # Extraer mensaje principal sin metadatos
        if "[source=" in error_message:
            main_msg = error_message.split("[source=")[0].strip()
        else:
            main_msg = error_message
        
        st.error(f"❌ **Error obteniendo datos de mercado**: {main_msg}")
        
        if symbol:
            st.warning(f"⚠️ **Problema con símbolo**: '{symbol}'")
            suggestions = _get_symbol_suggestions(symbol, source_name)
            with st.expander("💡 Sugerencias"):
                st.markdown(suggestions)
        
        # Sugerencias adicionales según el tipo de error
        if "timeout" in error_message.lower() or "time" in error_message.lower():
            st.info("🌐 **Problema de conexión**: Verifica tu conexión a Internet y vuelve a intentar")
        elif "rate limit" in error_message.lower() or "429" in error_message:
            st.info("⏱️ **Límite de peticiones**: Espera unos minutos antes de intentar nuevamente")
        elif params:
            st.info(f"📅 **Verifica el rango de fechas**: {params.fecha_ini} a {params.fecha_fin}")
    
    else:
        error_message = str(error)
        st.error(f"❌ **Error inesperado**: {error_message}")
        
        with st.expander("🔍 Detalles técnicos del error"):
            st.code(traceback.format_exc())
        
        st.info("💡 **Posibles soluciones**:")
        st.markdown("""
        - Verifica tu conexión a Internet
        - Asegúrate de que los símbolos sean válidos para la fuente seleccionada
        - Intenta con un rango de fechas más pequeño o más reciente
        - Si el problema persiste, reinicia la aplicación
        """)


def _fetch_data_with_spinner(params: DatosParams, symbols_list: list[str]) -> dict:
    """Descarga datos del mercado con spinner."""
    cfg_dict, kind = build_cfg_and_kind(
        params.fuente,
        params.tipo,
        params.intervalo,
    )
    
    with st.spinner("Descargando datos de mercado..."):
        data_map = fetch_market_data(
            cfg_dict=cfg_dict,
            symbols=symbols_list,
            start=params.fecha_ini,
            end=params.fecha_fin,
            interval=params.intervalo,
            kind=kind,
        )
    
    return data_map


def _process_and_download_data(params: DatosParams) -> dict:
    """Procesa y descarga datos del mercado."""
    symbols_list = _parse_and_validate_symbols(params.simbolos)
    
    if not symbols_list:
        return {}
    
    return _fetch_data_with_spinner(params, symbols_list)


def _should_display_symbol_info(submit: bool, params: DatosParams | None, simbolos_texto: str) -> bool:
    """Determina si se debe mostrar la información de símbolos."""
    return not submit or not params or not simbolos_texto or not simbolos_texto.strip()


def _handle_form_submit(params: DatosParams) -> None:
    """Maneja el envío del formulario."""
    if not params.simbolos or not params.simbolos.strip():
        return
    
    try:
        logger.info(f"📥 Descargando datos - fuente: {params.fuente}, tipo: {params.tipo}")
        logger.debug(f"  Parámetros: símbolos={params.simbolos}, intervalo={params.intervalo}")
        logger.debug(f"  Fechas: {params.fecha_ini} a {params.fecha_fin}")
        
        data_map = _process_and_download_data(params)
        
        if not data_map:
            logger.warning("No se recibieron datos del backend")
            # No mostrar error aquí ya que _handle_extraction_error se encarga si hubo excepción
            # Solo mostrar advertencia si no hubo excepción pero tampoco datos
            return
        
        logger.info(f"✅ Datos recibidos: {len(data_map)} símbolos")
        logger.debug(f"  Símbolos en data_map: {list(data_map.keys())}")
        
        for symbol, data_info in data_map.items():
            if isinstance(data_info, dict) and "data" in data_info:
                df = data_info["data"]
                logger.debug(f"  {symbol}: shape={df.shape}, fechas={df.index.min()} a {df.index.max()}")
                logger.debug(f"    Columnas: {list(df.columns)}")
                logger.debug(f"    Valores NaN: {df.isna().sum().sum()}")
                close_col = df.get('Close') if 'Close' in df.columns else df.get('close', pd.Series())
                if not close_col.empty:
                    logger.debug(f"    Primeros valores Close: {close_col.head(3).tolist()}")
        
        _clear_old_cache()
        st.session_state["last_data_map"] = data_map
        _, kind = build_cfg_and_kind(params.fuente, params.tipo, params.intervalo)
        st.session_state["last_kind"] = kind
        
        logger.debug(f"  Tipo de datos guardado: {kind}")
        
        _data_map(data_map, kind)
        
        st.success(f"✅ **Datos descargados exitosamente**: {len(data_map)} símbolo(s) disponible(s)")
        
    except Exception as e:
        logger.error(f"Error obteniendo datos: {e}", exc_info=True)
        _handle_extraction_error(e, params)


def _display_cached_data() -> None:
    """Muestra los datos cacheados."""
    if "last_data_map" in st.session_state:
        st.info("📊 **Mostrando últimos datos descargados** (cache local)")
        data_map = st.session_state["last_data_map"]
        kind = st.session_state.get("last_kind", "ohlcv")
        _data_map(data_map, kind)


def tab_datos(submit: bool, params: DatosParams | None) -> None:
    """Contenido central de la pestaña 📊 Datos."""
    st.subheader("📊 Vista de datos")
    
    # Input de símbolos en el panel central (más espacio para ver todos)
    render_symbol_input("datos_simbolos")
    
    # Validar que haya símbolos si se está pulsando el botón
    simbolos_texto = st.session_state.get("datos_simbolos", "")
    if submit and params is not None and (not simbolos_texto or not simbolos_texto.strip()):
        st.error("❌ **Error:** Debes configurar al menos un símbolo antes de obtener datos.")
        st.divider()
    
    # Mostrar información de símbolos si corresponde
    if _should_display_symbol_info(submit, params, simbolos_texto):
        display_symbol_info(contexto="datos")
    
    st.divider()
    
    # Manejar envío del formulario o mostrar datos cacheados
    if submit and params is not None:
        _handle_form_submit(params)
    else:
        _display_cached_data()


def _data_map(data_map: dict, kind: str) -> None:
    """
    Renderiza tablas y gráficos rápidos para el resultado normalizado.
    `data_map`: Dict[str, dict] con formato serializable del cache.
    Optimizado para reducir uso de memoria.
    """
    for sym, data_info in data_map.items():
        st.markdown(f"### {sym}")

        # Manejar el nuevo formato serializable
        if isinstance(data_info, dict) and "data" in data_info:
            df = data_info["data"]
        else:
            # Fallback para formato anterior
            df = getattr(data_info, "data", None)
        
        if df is None:
            # Fallback: mostrar objeto tal cual si no tiene .data
            st.write(data_info)
            continue

        # Mostrar todos los datos del rango seleccionado con altura personalizada
        st.dataframe(df, height=400, width='stretch')
        
        # Mostrar información del rango de fechas
        _display_date_range_info(df)

        # Gráficos optimizados - mostrar todos los datos
        _render_charts(df, kind)


def _render_charts(df: pd.DataFrame, kind: str) -> None:
    """Renderiza gráficos según el tipo de datos."""
    if kind == "ohlcv":
        _render_ohlcv_chart(df)
    else:
        _render_series_chart(df)


def _render_ohlcv_chart(df: pd.DataFrame) -> None:
    """Renderiza gráfico de precios OHLCV."""
    close_col = next((c for c in df.columns if c.lower() == "close"), None)
    if close_col:
        st.line_chart(df[close_col])
    elif "Close" in df.columns:
        st.line_chart(df["Close"])


def _render_series_chart(df: pd.DataFrame) -> None:
    """Renderiza gráfico de series temporales."""
    if isinstance(df, pd.Series):
        st.line_chart(df)
    elif "value" in getattr(df, "columns", []):
        st.line_chart(df["value"])
