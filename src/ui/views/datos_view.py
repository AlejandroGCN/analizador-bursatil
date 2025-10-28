from __future__ import annotations
import streamlit as st
import pandas as pd
from ui.app_config import build_cfg_and_kind
from ui.services_backend import fetch_market_data
from ui.sidebars import DatosParams
from ui.utils import display_symbol_info, render_symbol_input


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


def _process_and_download_data(params: DatosParams) -> dict:
    """Procesa y descarga datos del mercado."""
    cfg_dict, kind = build_cfg_and_kind(
        params.fuente,
        params.tipo,
        params.intervalo,
    )
    
    symbols_list = [s.strip() for s in params.simbolos.replace(" ", ",").split(",") if s.strip()]
    
    for symbol in symbols_list:
        if not _validate_symbol_format(symbol):
            st.warning(f"⚠️ Advertencia: '{symbol}' parece mal formateado. Verifica que usas comas: 'MSFT, GOOGL'")
    
    if not symbols_list:
        st.error("❌ **Error:** No se pudieron parsear los símbolos. Verifica el formato.")
        return {}
    
    with st.spinner("Cargando datos…"):
        data_map = fetch_market_data(
            cfg_dict=cfg_dict,
            symbols=symbols_list,
            start=params.fecha_ini,
            end=params.fecha_fin,
            interval=params.intervalo,
            kind=kind,
        )
    
    return data_map


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
    
    # Mostrar información de símbolos (solo si no hay símbolos configurados y NO se ha pulsado el botón)
    if not submit or not params or not simbolos_texto or not simbolos_texto.strip():
        display_symbol_info("datos_simbolos", contexto="datos")
    
    st.divider()

    # Cuando el usuario envía el formulario del sidebar de Datos
    if submit and params is not None:
        if not params.simbolos or not params.simbolos.strip():
            return
        
        try:
            data_map = _process_and_download_data(params)

            if not data_map:
                st.warning("No se recibieron datos.")
                return

            _clear_old_cache()
            st.session_state["last_data_map"] = data_map
            cfg_dict, kind = build_cfg_and_kind(params.fuente, params.tipo, params.intervalo)
            st.session_state["last_kind"] = kind

            _data_map(data_map, kind)

        except Exception as e:
            error_msg = str(e)
            if error_msg.startswith("❌"):
                st.error(error_msg)
            else:
                st.error(f"❌ Error obteniendo datos: {e}")

    # Si no hay submit, intenta mostrar el último resultado cacheado
    elif "last_data_map" in st.session_state:
        st.info("Mostrando últimos datos descargados (cache).")
        data_map = st.session_state["last_data_map"]
        kind = st.session_state.get("last_kind", "ohlcv")
        _data_map(data_map, kind)


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

