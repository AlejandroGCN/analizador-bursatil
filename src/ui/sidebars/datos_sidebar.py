"""
Sidebar para la pestaña de Datos.

Muestra los intervalos disponibles dinámicamente según la fuente de datos seleccionada,
garantizando que solo se muestren los intervalos realmente soportados por cada adaptador.
"""
from __future__ import annotations
from typing import Tuple, Dict, List
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


def _get_allowed_intervals_for_source(source_key: str) -> List[str]:
    """
    Obtiene los intervalos permitidos para una fuente de datos.
    
    Consulta directamente los adaptadores para obtener los intervalos realmente
    soportados, garantizando que solo se muestren opciones válidas.
    
    Args:
        source_key: Clave de la fuente (ej: "yahoo", "binance", "tiingo")
    
    Returns:
        Lista de intervalos permitidos ordenados
    
    """
    try:
        from data_extractor.core.registry import REGISTRY
        
        # Obtener la clase Provider desde el registro
        provider_class = REGISTRY.get(source_key)
        if provider_class:
            # Instanciar temporalmente el provider para acceder al adapter
            provider = provider_class()
            if hasattr(provider, 'adapter') and hasattr(provider.adapter, 'allowed_intervals'):
                intervals = list(provider.adapter.allowed_intervals)
                
                # Ordenar intervalos de MAYOR a MENOR
                interval_order = [
                    "1mo", "1M",           # Mensual
                    "1wk", "1w",           # Semanal
                    "3d",                  # 3 días
                    "1d",                  # Diario
                    "12h",                 # 12 horas
                    "8h",                  # 8 horas
                    "6h",                  # 6 horas
                    "4h",                  # 4 horas
                    "2h",                  # 2 horas
                    "90m",                 # 90 minutos
                    "1h",                  # 1 hora
                    "60m",                 # 60 minutos
                    "30m",                 # 30 minutos
                    "15m",                 # 15 minutos
                    "5m",                  # 5 minutos
                    "3m",                  # 3 minutos
                    "1m"                   # 1 minuto
                ]
                
                # Ordenar según el orden definido (mayor a menor)
                sorted_intervals = sorted(
                    intervals, 
                    key=lambda x: interval_order.index(x) if x in interval_order else 999
                )
                
                return sorted_intervals
    except Exception as e:
        # Fallback: usar valores por defecto si no se puede obtener el adaptador
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"No se pudo obtener intervalos dinámicos para {source_key}: {e}")
    
    # Valores por defecto según fuente conocida (ordenados de mayor a menor)
    default_intervals = {
        "yahoo": ["1mo", "1wk", "1d", "90m", "1h", "60m", "30m", "15m", "5m", "1m"],
        "binance": ["1M", "1w", "3d", "1d", "12h", "8h", "6h", "4h", "2h", "1h", "30m", "15m", "5m", "3m", "1m"],
        "tiingo": ["1d"]  # Tiingo free tier solo soporta datos diarios
    }
    
    return default_intervals.get(source_key, ["1d"])


def _get_available_intervals_by_source() -> Dict[str, List[str]]:
    """
    Obtiene los intervalos disponibles para cada fuente de datos.
    
    Returns:
        Diccionario con fuente (clave UI) -> lista de intervalos permitidos
    """
    intervals_map = {}
    
    for ui_label, source_key in SOURCE_MAP.items():
        intervals_map[ui_label] = _get_allowed_intervals_for_source(source_key)
    
    return intervals_map


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
    
    # Mensajes informativos FUERA del formulario para no ocupar espacio
    fuente_actual = st.session_state.get("fuente_datos", available_sources[0])
    intervalo_actual = st.session_state.get("intervalo_datos", "1d")
    is_intraday = intervalo_actual in ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "60m", "90m"]
    
    if fuente_actual == "Tiingo" and "Tiingo" in available_sources:
        st.sidebar.info("ℹ️ Tiingo: Datos diarios de calidad institucional")
    elif fuente_actual == "Binance":
        st.sidebar.info("ℹ️ Binance: Datos intradía desde 1 minuto")
    elif fuente_actual == "Yahoo":
        if is_intraday:
            st.sidebar.warning("⚠️ **Intradía**: Máximo 7 días")
        else:
            st.sidebar.info("ℹ️ Yahoo: Datos históricos sin límite")
    
    # Formulario principal (SIDEBAR - widgets dentro del form NO usan .sidebar)
    with st.sidebar.form("form_datos"):
        st.selectbox("Fuente de datos:", available_sources, key="fuente_datos")
        
        st.date_input("Fecha inicio", pd.to_datetime("2020-01-01"), key="fecha_ini_datos", format="DD/MM/YYYY")
        st.date_input("Fecha fin", pd.to_datetime("2025-01-01"), key="fecha_fin_datos", format="DD/MM/YYYY")
        
        # Obtener intervalos disponibles dinámicamente según la fuente
        intervalos_por_fuente = _get_available_intervals_by_source()
        
        # Leer fuente actual del session state
        fuente_form = st.session_state.get("fuente_datos", available_sources[0])
        intervalos_disponibles = intervalos_por_fuente.get(fuente_form, ["1d"])
        
        # Validar que el intervalo seleccionado sigue disponible después de cambiar de fuente
        intervalo_form = st.session_state.get("intervalo_datos", "1d")
        if intervalo_form not in intervalos_disponibles:
            st.session_state["intervalo_datos"] = "1d"
            intervalo_form = "1d"
        
        # Mostrar solo intervalos realmente disponibles para esta fuente
        index_default = 0
        if intervalo_form in intervalos_disponibles:
            index_default = intervalos_disponibles.index(intervalo_form)
        
        st.selectbox(
            "Intervalo", 
            intervalos_disponibles, 
            key="intervalo_datos",
            index=index_default,
            help=f"{len(intervalos_disponibles)} intervalos disponibles. 1d=diario, 1h=horario."
        )
        st.selectbox(
            "Tipo", 
            ["Precios Históricos", "Retornos"], 
            key="tipo_datos",
            help="Precios: valores OHLCV | Retornos: cambios porcentuales diarios"
        )
        
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

