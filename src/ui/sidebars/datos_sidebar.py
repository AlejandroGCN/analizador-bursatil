from __future__ import annotations
from typing import Tuple
import streamlit as st
import pandas as pd
from ui.app_config import SOURCE_MAP
from .types import DatosParams
from ui.utils import (
    validate_and_clean_symbols,
    apply_sidebar_styles,
    render_symbol_import_controls,
    render_file_upload_controls
)


def sidebar_datos() -> Tuple[bool, DatosParams]:
    """Sidebar para la pestaña de Datos."""
    st.sidebar.header("⚙️ Parámetros de datos")
    
    # Aplicar estilos del sidebar (función reutilizable)
    apply_sidebar_styles()
    
    # Obtener fuentes disponibles dinámicamente
    available_sources = list(SOURCE_MAP.keys())
    
    # Controles de importación de símbolos (función reutilizable)
    render_symbol_import_controls(
        source_key="cartera_symbols",
        target_key="datos_simbolos",
        from_label="Cartera",
        button_label="💼 Importar símbolos desde Cartera"
    )
    
    # Controles de carga de archivos (función reutilizable)
    render_file_upload_controls(
        target_key="datos_simbolos",
        button_label="📁 Cargar símbolos desde archivo",
        uploader_key="file_uploader_datos"
    )
    
    st.sidebar.markdown("---")
    
    # Formulario principal (SIDEBAR - widgets dentro del form NO usan .sidebar)
    with st.sidebar.form("form_datos"):
        st.selectbox("Fuente de datos:", available_sources, key="fuente_datos")
        
        st.date_input("Fecha inicio", pd.to_datetime("2020-01-01"), key="fecha_ini_datos")
        st.date_input("Fecha fin", pd.to_datetime("2025-01-01"), key="fecha_fin_datos")
        
        # Intervalos disponibles según la fuente seleccionada
        intervalos_por_fuente = {
            "Yahoo": ["1d", "1h", "1wk", "1mo", "1m", "5m", "15m", "30m"],
            "Binance": ["1d", "1h", "1w", "1M", "1m", "3m", "5m", "15m", "30m", "2h", "4h", "6h", "8h", "12h", "3d"],
        }
        
        # Añadir Stooq solo si está disponible
        if "Stooq" in available_sources:
            intervalos_por_fuente["Stooq"] = ["1d", "1wk", "1mo"]
        
        # Leer fuente actual del session state
        fuente_actual = st.session_state.get("fuente_datos", available_sources[0])
        intervalos_disponibles = intervalos_por_fuente.get(fuente_actual, ["1d", "1h", "1wk"])
        
        # Mostrar información sobre intervalos disponibles
        if fuente_actual == "Stooq" and "Stooq" in available_sources:
            st.info("ℹ️ Stooq solo soporta datos diarios (no intradía)")
        elif fuente_actual == "Binance":
            st.info("ℹ️ Binance soporta datos intradía desde 1 minuto")
        
        st.selectbox("Intervalo", intervalos_disponibles, key="intervalo_datos")
        st.selectbox("Tipo", ["Precios Históricos", "Retornos"], key="tipo_datos")
        
        submitted = st.form_submit_button(
            "📥 Obtener datos",
            width='stretch'
        )
    
    # Obtener valores para construir DatosParams
    simbolos = st.session_state.get("datos_simbolos", "")
    fuente = st.session_state.get("fuente_datos", available_sources[0])
    
    return submitted, DatosParams(
        fuente,
        simbolos,
        st.session_state.get("fecha_ini_datos", pd.to_datetime("2020-01-01")),
        st.session_state.get("fecha_fin_datos", pd.to_datetime("2025-01-01")),
        st.session_state.get("intervalo_datos", "1d"),
        st.session_state.get("tipo_datos", "Precios Históricos")
    )

