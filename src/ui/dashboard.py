# src/ui/dashboard.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analizador Bursátil", layout="wide")
st.title("📈 Analizador Bursátil")

# ────────────────────────────────
# Pestañas principales
# ────────────────────────────────
TABS = ["📊 Datos", "💼 Cartera", "🎲 Monte Carlo", "📋 Reporte", "⚙️ Configuración"]

# Inicializa estado
if "active_tab" not in st.session_state:
    st.session_state.active_tab = TABS[0]

# Muestra pestañas tipo radio horizontal
selected_tab = st.radio(
    "Secciones",
    options=TABS,
    index=TABS.index(st.session_state.active_tab),
    horizontal=True,
    label_visibility="collapsed",
)

# Si el usuario cambió de pestaña → actualiza estado y rerun inmediato
if selected_tab != st.session_state.active_tab:
    st.session_state.active_tab = selected_tab
    st.rerun()

tab = st.session_state.active_tab

# ────────────────────────────────
# Sidebars dinámicos por pestaña
# ────────────────────────────────
def sidebar_datos():
    st.sidebar.header("⚙️ Parámetros de datos")
    st.sidebar.selectbox("Fuente de datos:", ["Yahoo", "Alpha Vantage", "Binance"], key="fuente_datos")
    st.sidebar.text_input("Símbolos:", "AAPL,MSFT", key="simbolos_datos")
    st.sidebar.date_input("Fecha inicio", pd.to_datetime("2020-01-01"), key="fecha_ini_datos")
    st.sidebar.date_input("Fecha fin", pd.to_datetime("2025-01-01"), key="fecha_fin_datos")
    st.sidebar.selectbox("Intervalo", ["1d", "1h", "1wk"], key="intervalo_datos")
    st.sidebar.selectbox("Tipo", ["OHLCV", "Volatilidad", "Returns"], key="tipo_datos")
    st.sidebar.button("Obtener datos", key="btn_get_datos")

def sidebar_cartera():
    st.sidebar.header("💼 Parámetros de cartera")
    st.sidebar.text_input("Activos (coma)", "AAPL,MSFT,GOOG", key="cartera_symbols")
    st.sidebar.text_input("Pesos (coma)", "0.33,0.33,0.34", key="cartera_weights")
    st.sidebar.button("Aplicar pesos", key="cartera_apply")

def sidebar_montecarlo():
    st.sidebar.header("🎲 Parámetros Monte Carlo")
    st.sidebar.number_input("Nº de simulaciones", 100, 10_000, 1000, key="mc_nsims")
    st.sidebar.number_input("Horizonte (días)", 1, 365, 252, key="mc_horizonte")
    st.sidebar.checkbox("¿Volatilidad dinámica?", key="mc_vol_dyn")
    st.sidebar.button("Lanzar simulación", key="mc_run")

def sidebar_reporte():
    st.sidebar.header("📋 Opciones de reporte")
    st.sidebar.selectbox("Formato", ["Markdown", "HTML", "PDF (WIP)"], key="reporte_fmt")
    st.sidebar.checkbox("Incluir métricas de riesgo", value=True, key="reporte_risk")
    st.sidebar.button("Generar reporte", key="reporte_build")

def sidebar_config():
    st.sidebar.header("⚙️ Configuración avanzada")
    st.sidebar.text_input("API Key (Alpha Vantage)", key="cfg_av_key")
    st.sidebar.text_input("API Key (Binance)", key="cfg_binance_key")
    st.sidebar.selectbox("Normalización", ["Sí", "No"], key="cfg_norm")

# Renderiza el sidebar correspondiente
if tab == "📊 Datos":
    sidebar_datos()
elif tab == "💼 Cartera":
    sidebar_cartera()
elif tab == "🎲 Monte Carlo":
    sidebar_montecarlo()
elif tab == "📋 Reporte":
    sidebar_reporte()
elif tab == "⚙️ Configuración":
    sidebar_config()
else:
    st.sidebar.empty()

# ────────────────────────────────
# Contenido central por pestaña
# ────────────────────────────────
if tab == "📊 Datos":
    st.subheader("📊 Vista de datos")
    st.info("Aquí se mostrarán los datos descargados.")
elif tab == "💼 Cartera":
    st.subheader("💼 Construcción de cartera")
    st.info("Selecciona activos y asigna pesos.")
elif tab == "🎲 Monte Carlo":
    st.subheader("🎲 Simulación Monte Carlo")
    st.info("Resultados y gráficos de simulación.")
elif tab == "📋 Reporte":
    st.subheader("📋 Reporte")
    st.info("Informe resumen del análisis.")
elif tab == "⚙️ Configuración":
    st.subheader("⚙️ Configuración avanzada")
    st.info("Ajusta parámetros globales y claves API.")
