from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, Any, Dict, Callable
from ui.app_config import TAB_LABELS
from ui.file_loader import load_symbols_from_file
import streamlit as st
import pandas as pd

# ───────────────────────────────────────────────────────────────
# Tipos de retorno
# ───────────────────────────────────────────────────────────────
@dataclass
class DatosParams:
    fuente: str
    simbolos: str
    fecha_ini: Optional[pd.Timestamp]
    fecha_fin: Optional[pd.Timestamp]
    intervalo: str
    tipo: str

@dataclass
class CarteraParams:
    symbols: str
    weights: str

@dataclass
class MonteCarloParams:
    nsims: int
    horizonte: int
    vol_dinamica: bool

@dataclass
class ReporteParams:
    formato: str
    incluir_riesgo: bool

@dataclass
class ConfigParams:
    normalizacion: str

# ───────────────────────────────────────────────────────────────
# Formularios del sidebar
# ───────────────────────────────────────────────────────────────
def sidebar_datos() -> Tuple[bool, DatosParams]:
    if "simbolos" not in st.session_state:
        st.session_state.simbolos = "AAPL,MSFT"

    load_message = st.empty()

    with st.sidebar.form("form_datos"):
        st.header("⚙️ Parámetros de datos")
        # Obtener fuentes disponibles dinámicamente
        from ui.app_config import SOURCE_MAP
        available_sources = list(SOURCE_MAP.keys())
        fuente = st.selectbox("Fuente de datos:", available_sources, key="fuente_datos")

        with st.expander("📁 Cargar símbolos desde archivo", expanded=False):
            uploaded_file = st.file_uploader(
                "Selecciona un archivo",
                type=['csv', 'xlsx', 'xls', 'json', 'txt'],
                help="Formatos soportados: CSV, Excel, JSON, TXT",
                key="file_uploader"
            )
            load_clicked = st.form_submit_button("🔄 Cargar símbolos", key="load_symbols")

        if uploaded_file is not None and load_clicked:
            try:
                symbols = load_symbols_from_file(uploaded_file)
                if symbols:
                    st.session_state.simbolos = ",".join(symbols)
                    load_message.success(f"✅ {len(symbols)} símbolos cargados: {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
                else:
                    load_message.error("❌ No se encontraron símbolos en el archivo")
            except Exception as e:
                load_message.error(f"❌ Error procesando archivo: {str(e)}")
        elif load_clicked:
            load_message.warning("⚠️ Primero selecciona un archivo")

        simbolos = st.text_input("Símbolos:", key="simbolos")

        fecha_ini = st.date_input("Fecha inicio", pd.to_datetime("2020-01-01"), key="fecha_ini_datos")
        fecha_fin = st.date_input("Fecha fin", pd.to_datetime("2025-01-01"), key="fecha_fin_datos")
        # Intervalos disponibles según la fuente seleccionada
        intervalos_por_fuente = {
            "Yahoo": ["1d", "1h", "1wk", "1mo", "1m", "5m", "15m", "30m"],
            "Binance": ["1d", "1h", "1wk", "1mo", "1m", "3m", "5m", "15m", "30m", "2h", "4h", "6h", "8h", "12h"],
        }
        
        # Añadir Stooq solo si está disponible
        if "Stooq" in available_sources:
            intervalos_por_fuente["Stooq"] = ["1d", "1wk", "1mo"]
        
        intervalos_disponibles = intervalos_por_fuente.get(fuente, ["1d", "1h", "1wk"])
        
        # Mostrar información sobre intervalos disponibles
        if fuente == "Stooq" and "Stooq" in available_sources:
            st.info("ℹ️ Stooq solo soporta datos diarios (no intradía)")
        elif fuente == "Binance":
            st.info("ℹ️ Binance soporta datos intradía desde 1 minuto")
        
        intervalo = st.selectbox("Intervalo", intervalos_disponibles, key="intervalo_datos")
        tipo = st.selectbox("Tipo", ["Precios Históricos", "Retornos"], key="tipo_datos")
        submitted = st.form_submit_button("Obtener datos")

        return submitted, DatosParams(fuente, simbolos, fecha_ini, fecha_fin, intervalo, tipo)


def sidebar_cartera() -> Tuple[bool, CarteraParams]:
    with st.sidebar.form("form_cartera"):
        st.header("💼 Parámetros de cartera")
        symbols = st.text_input("Activos (coma)", "AAPL,MSFT,GOOG", key="cartera_symbols")
        weights = st.text_input("Pesos (coma)", "0.33,0.33,0.34", key="cartera_weights")
        submitted = st.form_submit_button("Aplicar pesos")
    return submitted, CarteraParams(symbols, weights)


def sidebar_montecarlo() -> Tuple[bool, MonteCarloParams]:
    with st.sidebar.form("form_montecarlo"):
        st.header("🎲 Parámetros Monte Carlo")
        nsims = st.number_input("Nº de simulaciones", 100, 10_000, 1000, key="mc_nsims")
        horizonte = st.number_input("Horizonte (días)", 1, 365, 252, key="mc_horizonte")
        vol_dyn = st.checkbox("¿Volatilidad dinámica?", key="mc_vol_dyn")
        submitted = st.form_submit_button("Lanzar simulación")
    return submitted, MonteCarloParams(int(nsims), int(horizonte), bool(vol_dyn))


def sidebar_reporte() -> Tuple[bool, ReporteParams]:
    with st.sidebar.form("form_reporte"):
        st.header("📋 Opciones de reporte")
        formato = st.selectbox("Formato", ["Markdown", "HTML", "PDF (WIP)"], key="reporte_fmt")
        incluir_riesgo = st.checkbox("Incluir métricas de riesgo", value=True, key="reporte_risk")
        submitted = st.form_submit_button("Generar reporte")
    return submitted, ReporteParams(formato, incluir_riesgo)


def sidebar_config() -> Tuple[bool, ConfigParams]:
    with st.sidebar.form("form_config"):
        st.header("⚙️ Configuración avanzada")
        normalizacion = st.selectbox("Normalización", ["Sí", "No"], key="cfg_norm")
        submitted = st.form_submit_button("Guardar configuración")
    return submitted, ConfigParams(normalizacion)


TAB_TO_SIDEBAR: Dict[str, Callable[[], Tuple[bool, Any]]] = {
    TAB_LABELS["datos"]: sidebar_datos,
    TAB_LABELS["cartera"]: sidebar_cartera,
    TAB_LABELS["montecarlo"]: sidebar_montecarlo,
    TAB_LABELS["reporte"]: sidebar_reporte,
    TAB_LABELS["config"]: sidebar_config,
}

def sidebar_for(tab: str) -> Tuple[bool, Any]:
    fn = TAB_TO_SIDEBAR.get(tab)
    if fn is None:
        st.sidebar.empty()
        return False, None
    return fn()
