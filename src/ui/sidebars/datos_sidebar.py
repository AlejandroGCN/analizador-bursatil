from __future__ import annotations
from typing import Tuple
import streamlit as st
import pandas as pd
from ui.app_config import SOURCE_MAP
from .types import DatosParams
from ui.utils import validate_and_clean_symbols


def sidebar_datos() -> Tuple[bool, DatosParams]:
    """Sidebar para la pestaña de Datos."""
    st.sidebar.header("⚙️ Parámetros de datos")
    
    # CSS para sidebar un poco más oscuro
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #d4e4f7;
    }
    [data-testid="stSidebar"] > div {
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Obtener fuentes disponibles dinámicamente
    available_sources = list(SOURCE_MAP.keys())
    
    # Botón de importar desde cartera (ANTES de crear el widget)
    btn_import = st.sidebar.button("💼 Importar símbolos desde Cartera", key="btn_import_datos", width='stretch')
    
    if btn_import:
        cartera_symbols = st.session_state.get("cartera_symbols", "")
        if cartera_symbols and cartera_symbols.strip():
            st.session_state.datos_simbolos = cartera_symbols
            st.success("✅ Símbolos importados desde Cartera")
        else:
            st.warning("⚠️ No hay símbolos en Cartera para importar")
    
    # Sección de carga de archivos
    uploaded_file = st.sidebar.file_uploader(
        "Selecciona un archivo",
        type=['csv', 'xlsx', 'xls', 'json', 'txt'],
        help="Formatos: CSV, Excel, JSON, TXT",
        key="file_uploader_datos"
    )
    
    btn_load = st.sidebar.button("📁 Cargar símbolos desde archivo", key="btn_load_file_datos", width='stretch')
    
    if btn_load and uploaded_file is not None:
        try:
            from ui.file_loader import load_symbols_from_file
            symbols = load_symbols_from_file(uploaded_file)
            if symbols:
                st.session_state.datos_simbolos = ",".join(symbols)
                st.success(f"✅ {len(symbols)} símbolos cargados")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    elif btn_load:
        st.warning("⚠️ Primero selecciona un archivo")
    
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

