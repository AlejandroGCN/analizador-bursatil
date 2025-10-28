from __future__ import annotations
import streamlit as st
import pandas as pd
from ui.app_config import build_cfg_and_kind
from ui.services_backend import fetch_market_data
from ui.sidebars import DatosParams
from ui.utils import display_symbol_info

def tab_datos(submit: bool, params: DatosParams | None) -> None:
    """Contenido central de la pestaña 📊 Datos."""
    st.subheader("📊 Vista de datos")
    
    # Input de símbolos en el panel central (más espacio para ver todos)
    st.text_input(
        "📝 Símbolos:", 
        key="datos_simbolos",
        placeholder="Ej: AAPL, MSFT, GOOGL",
        help="Escribe los símbolos separados por coma (ej: AAPL, MSFT, GOOGL)",
        label_visibility="visible"
    )
    
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
        # Validar que haya símbolos configurados (ANTES del try)
        if not params.simbolos or not params.simbolos.strip():
            return
        
        try:
            # Traducir etiquetas de la UI a claves internas y construir cfg
            cfg_dict, kind = build_cfg_and_kind(
                params.fuente,
                params.tipo,
                params.intervalo,
            )

            with st.spinner("Cargando datos…"):
                # Convertir string de símbolos a lista
                symbols_list = [s.strip() for s in params.simbolos.replace(" ", ",").split(",") if s.strip()]
                
                # Validar formato de símbolos
                for symbol in symbols_list:
                    if "." in symbol and not any(symbol.endswith(f".{ext}") for ext in ["US", "DE", "FR", "UK", "JP", "CA"]):
                        st.warning(f"⚠️ Advertencia: '{symbol}' parece mal formateado. Verifica que usas comas: 'MSFT, GOOGL'")
                
                # Validar nuevamente después de parsear
                if not symbols_list:
                    st.error("❌ **Error:** No se pudieron parsear los símbolos. Verifica el formato.")
                    return
                
                data_map = fetch_market_data(
                    cfg_dict=cfg_dict,
                    symbols=symbols_list,
                    start=params.fecha_ini,
                    end=params.fecha_fin,
                    interval=params.intervalo,
                    kind=kind,
                )

            if not data_map:
                st.warning("No se recibieron datos.")
                return

            # Limpiar cache anterior y resultados de simulaciones antiguos
            if "last_data_map" in st.session_state:
                del st.session_state["last_data_map"]
            
            # Limpiar simulaciones antiguos al obtener datos nuevos (pero mantener cartera)
            if "montecarlo_results" in st.session_state:
                del st.session_state["montecarlo_results"]
            if "montecarlo_portfolio" in st.session_state:
                del st.session_state["montecarlo_portfolio"]
            if "reporte_portfolio" in st.session_state:
                del st.session_state["reporte_portfolio"]
            
            # Persistir resultado
            st.session_state["last_data_map"] = data_map
            st.session_state["last_kind"] = kind

            _data_map(data_map, kind)

        except Exception as e:
            error_msg = str(e)
            # Si el mensaje ya tiene formato con emojis, mostrarlo tal cual
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
        if not df.empty:
            st.info(f"📅 **Rango de datos:** {df.index.min().strftime('%Y-%m-%d')} a {df.index.max().strftime('%Y-%m-%d')} ({len(df)} registros)")

        # Gráficos optimizados - mostrar todos los datos
        if kind == "ohlcv":
            # Busca columna de cierre con tolerancia a capitalización
            close_col = next((c for c in df.columns if c.lower() == "close"), None)
            if close_col:
                chart_data = df[close_col]
                st.line_chart(chart_data)
            elif "Close" in df.columns:
                chart_data = df["Close"]
                st.line_chart(chart_data)
        else:
            if isinstance(df, pd.Series):
                chart_data = df
                st.line_chart(chart_data)
            elif "value" in getattr(df, "columns", []):
                chart_data = df["value"]
                st.line_chart(chart_data)

