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
        source: Fuente de datos (yahoo, binance, tiingo)
    
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
    elif source.lower() == "tiingo":
        suggestions.extend([
            f"Verifica que '{symbol}' existe en Tiingo",
            "Tiingo requiere API key gratuita (ver TIINGO_SETUP.md)",
            "Símbolos USA: AAPL, MSFT, GOOGL (sin sufijos)",
            "Símbolos internacionales pueden requerir sufijos (.LON para UK, .DEX para Alemania)"
        ])
    
    return "\n".join(f"- {s}" for s in suggestions)


def _display_source_examples(source_name: str) -> None:
    """Muestra ejemplos de símbolos válidos según la fuente."""
    source_lower = source_name.lower()
    if source_lower == "yahoo":
        st.code("AAPL, MSFT, GOOGL, TSLA, AMZN  # Acciones US\nSIEMENS.DE, ASML.AS  # Acciones internacionales")
    elif source_lower == "binance":
        st.code("BTCUSDT, ETHUSDT, BNBBTC  # Pares de criptomonedas")
    else:
        st.code("AAPL, MSFT, GOOGL, BP  # Tiingo (requiere API key)")


def _handle_symbol_not_found(error: SymbolNotFound, source_name: str) -> None:
    """Maneja errores de símbolo no encontrado."""
    symbol = getattr(error, 'symbol', 'símbolo desconocido')
    st.error(f"🚫 **Símbolo no encontrado**: '{symbol}' no existe en {source_name}")
    
    suggestions = _get_symbol_suggestions(symbol, source_name)
    with st.expander("💡 Sugerencias para resolver el problema"):
        st.markdown(suggestions)
        st.markdown("**Ejemplos de símbolos válidos por fuente:**")
        _display_source_examples(source_name)


def _extract_main_error_message(error_message: str) -> str:
    """Extrae el mensaje principal de error sin metadatos."""
    if "[source=" in error_message:
        return error_message.split("[source=")[0].strip()
    return error_message


def _display_extraction_error_suggestions(error_message: str, params: DatosParams | None) -> None:
    """Muestra sugerencias adicionales según el tipo de error de extracción."""
    error_lower = error_message.lower()
    if "timeout" in error_lower or "time" in error_lower:
        st.info("🌐 **Problema de conexión**: Verifica tu conexión a Internet y vuelve a intentar")
    elif "rate limit" in error_lower or "429" in error_message:
        st.info("⏱️ **Límite de peticiones**: Espera unos minutos antes de intentar nuevamente")
    elif params:
        st.info(f"📅 **Verifica el rango de fechas**: {params.fecha_ini} a {params.fecha_fin}")


def _handle_extraction_error_case(error: ExtractionError, source_name: str, params: DatosParams | None) -> None:
    """Maneja errores genéricos de extracción."""
    symbol = getattr(error, 'symbol', None)
    error_message = str(error)
    main_msg = _extract_main_error_message(error_message)
    
    st.error(f"❌ **Error obteniendo datos de mercado**: {main_msg}")
    
    if symbol:
        st.warning(f"⚠️ **Problema con símbolo**: '{symbol}'")
        suggestions = _get_symbol_suggestions(symbol, source_name)
        with st.expander("💡 Sugerencias"):
            st.markdown(suggestions)
    
    _display_extraction_error_suggestions(error_message, params)


def _handle_unexpected_error(error: Exception) -> None:
    """Maneja errores inesperados."""
    error_message = str(error)
    
    # Registrar el error completo en los logs
    logger.error(f"Error inesperado: {error_message}", exc_info=True)
    
    # Mostrar solo mensaje de error al usuario (sin detalles técnicos)
    st.error(f"❌ **Error inesperado**: {error_message}")
    
    st.info("💡 **Posibles soluciones**:")
    st.markdown("""
    - Verifica tu conexión a Internet
    - Asegúrate de que los símbolos sean válidos para la fuente seleccionada
    - Intenta con un rango de fechas más pequeño o más reciente
    - Si el problema persiste, reinicia la aplicación
    """)


def _handle_extraction_error(error: Exception, params: DatosParams | None) -> None:
    """
    Maneja errores de extracción con mensajes informativos y sugerencias.
    
    Args:
        error: Excepción capturada
        params: Parámetros de descarga (opcional, para obtener información contextual)
    """
    source_name = params.fuente if params else "la fuente seleccionada"
    
    if isinstance(error, SymbolNotFound):
        _handle_symbol_not_found(error, source_name)
    elif isinstance(error, ExtractionError):
        _handle_extraction_error_case(error, source_name, params)
    else:
        _handle_unexpected_error(error)


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
                if isinstance(df, pd.DataFrame):
                    logger.debug(f"    Columnas: {list(df.columns)}")
                    logger.debug(f"    Valores NaN: {df.isna().sum().sum()}")
                    close_col = df.get('Close') if 'Close' in df.columns else df.get('close', pd.Series())
                    if not close_col.empty:
                        logger.debug(f"    Primeros valores Close: {close_col.head(3).tolist()}")
                else:
                    logger.debug(f"    Tipo: Series")
                    logger.debug(f"    Valores NaN: {df.isna().sum()}")
        
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
    if df.empty:
        st.warning("⚠️ No hay datos suficientes para graficar")
        return
    
    if kind == "ohlcv":
        _render_ohlcv_chart(df)
    else:
        _render_series_chart(df, kind)


def _render_ohlcv_chart(df: pd.DataFrame) -> None:
    """Renderiza gráfico de precios OHLCV mejorado."""
    import matplotlib.pyplot as plt
    
    if isinstance(df, pd.Series):
        st.subheader("📈 Evolución de Precios")
        st.line_chart(df, use_container_width=True)
    elif isinstance(df, pd.DataFrame):
        close_col = next((c for c in df.columns if c.lower() == "close"), None)
        
        if close_col:
            st.subheader("📈 Evolución del Precio de Cierre")
            
            # Crear gráfico mejorado con matplotlib
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df.index, df[close_col], linewidth=1.5, color='#1f77b4')
            ax.set_xlabel('Fecha', fontsize=10)
            ax.set_ylabel('Precio de Cierre', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
            plt.close(fig)
        elif "Close" in df.columns:
            st.subheader("📈 Evolución del Precio de Cierre")
            st.line_chart(df["Close"], use_container_width=True)


def _render_series_chart(df: pd.DataFrame, kind: str = "series") -> None:
    """Renderiza gráfico de series temporales mejorado."""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    
    # Determinar el título según el tipo de datos
    title_map = {
        "returns": "📊 Retornos Diarios",
        "volatility": "📉 Volatilidad",
        "performance": "📈 Performance",
        "volume": "📊 Volumen",
    }
    chart_title = title_map.get(kind, "📊 Serie Temporal")
    
    if isinstance(df, pd.Series):
        st.subheader(chart_title)
        
        # Crear gráfico mejorado con matplotlib para Series
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Usar barras para retornos (más visual)
        if kind == "returns" or "return" in str(chart_title).lower():
            colors = ['#d62728' if x < 0 else '#2ca02c' for x in df.values]
            ax.bar(df.index, df.values, width=1.5, color=colors, alpha=0.7, edgecolor='none')
            ax.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
        else:
            ax.plot(df.index, df.values, linewidth=1.5, color='#2ca02c', alpha=0.8)
            ax.fill_between(df.index, df.values, alpha=0.2, color='#2ca02c')
        
        # Mejorar el formato del eje X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        ax.set_xlabel('Fecha', fontsize=11, fontweight='bold')
        ax.set_ylabel('Valor', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        
        # Rotar etiquetas del eje X
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Ajustar márgenes
        plt.subplots_adjust(bottom=0.15, left=0.08, right=0.98, top=0.95)
        
        st.pyplot(fig)
        plt.close(fig)
        
    elif isinstance(df, pd.DataFrame):
        st.subheader(chart_title)
        
        # Determinar qué columna graficar
        if "value" in df.columns:
            col_to_plot = "value"
        elif "close" in df.columns:
            col_to_plot = "close"
        elif len(df.columns) > 0:
            col_to_plot = df.columns[0]
        else:
            st.warning("⚠️ No se encontró columna para graficar")
            return
        
        # Crear gráfico mejorado con matplotlib para DataFrame
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Usar barras para retornos (más visual)
        if kind == "returns" or "return" in col_to_plot.lower():
            colors = ['#d62728' if x < 0 else '#2ca02c' for x in df[col_to_plot].values]
            ax.bar(df.index, df[col_to_plot], width=1.5, color=colors, alpha=0.7, edgecolor='none')
            ax.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
        else:
            ax.plot(df.index, df[col_to_plot], linewidth=1.5, color='#2ca02c', alpha=0.8)
            ax.fill_between(df.index, df[col_to_plot], alpha=0.2, color='#2ca02c')
        
        # Mejorar el formato del eje X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        ax.set_xlabel('Fecha', fontsize=11, fontweight='bold')
        ax.set_ylabel(col_to_plot.capitalize(), fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        
        # Rotar etiquetas del eje X
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Ajustar márgenes
        plt.subplots_adjust(bottom=0.15, left=0.08, right=0.98, top=0.95)
        
        st.pyplot(fig)
        plt.close(fig)
