# src/ui/sidebars.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, Any, Dict, Callable
from ui.app_config import TAB_LABELS
import streamlit as st
import pandas as pd

# ───────────────────────────────────────────────────────────────
# Tipos de retorno (claridad al consumir en dashboard)
# ───────────────────────────────────────────────────────────────
@dataclass
class DatosParams:
    fuente: str
    simbolos: str
    fecha_ini: Optional[pd.Timestamp]
    fecha_fin: Optional[pd.Timestamp]
    intervalo: str
    tipo: str  # "OHLCV" | "Volatilidad" | "Returns"

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
    av_key: str
    binance_key: str
    normalizacion: str

# ───────────────────────────────────────────────────────────────
# Sidebars con FORM → devuelven (submitted, params)
# ───────────────────────────────────────────────────────────────
def sidebar_datos() -> Tuple[bool, DatosParams]:
    with st.sidebar.form("form_datos"):
        st.header("⚙️ Parámetros de datos")
        fuente = st.selectbox("Fuente de datos:", ["Yahoo", "Alpha Vantage", "Binance"], key="fuente_datos")
        simbolos = st.text_input("Símbolos:", "AAPL,MSFT", key="simbolos_datos")
        fecha_ini = st.date_input("Fecha inicio", pd.to_datetime("2020-01-01"), key="fecha_ini_datos")
        fecha_fin = st.date_input("Fecha fin", pd.to_datetime("2025-01-01"), key="fecha_fin_datos")
        intervalo = st.selectbox("Intervalo", ["1d", "1h", "1wk"], key="intervalo_datos")
        tipo = st.selectbox("Tipo", ["OHLCV", "Volatilidad", "Returns"], key="tipo_datos")
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
        av_key = st.text_input("API Key (Alpha Vantage)", key="cfg_av_key")
        binance_key = st.text_input("API Key (Binance)", key="cfg_binance_key")
        normalizacion = st.selectbox("Normalización", ["Sí", "No"], key="cfg_norm")
        submitted = st.form_submit_button("Guardar configuración")
    return submitted, ConfigParams(av_key, binance_key, normalizacion)

# ───────────────────────────────────────────────────────────────
# Despachador único por pestaña
# ───────────────────────────────────────────────────────────────
TAB_TO_SIDEBAR: Dict[str, Callable[[], Tuple[bool, Any]]] = {
    TAB_LABELS["datos"]: sidebar_datos,
    TAB_LABELS["cartera"]: sidebar_cartera,
    TAB_LABELS["montecarlo"]: sidebar_montecarlo,
    TAB_LABELS["reporte"]: sidebar_reporte,
    TAB_LABELS["config"]: sidebar_config,
}

def sidebar_for(tab: str) -> Tuple[bool, Any]:
    """
    Renderiza el sidebar correspondiente a `tab` y devuelve (submitted, params).
    Si la pestaña no tiene sidebar, devuelve (False, None).
    """
    fn = TAB_TO_SIDEBAR.get(tab)
    if fn is None:
        st.sidebar.empty()
        return False, None
    return fn()
