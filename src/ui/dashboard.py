# src/ui/dashboard.py
import os, sys
THIS_DIR = os.path.dirname(__file__)
SRC_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

import streamlit as st
import logging
from pathlib import Path
from logs.logs_handler import setup_logging_from_file, resolve_log_cfg

# Configurar logging desde archivo YAML
log_config_path = Path(__file__).parent.parent / "logs" / "logging.yaml"
setup_logging_from_file(resolve_log_cfg(str(log_config_path)))

# Reducir ruido de librerías externas
logging.getLogger("yfinance").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# ── imports principales ───────────────────────────────────────────────
from ui.sidebars import sidebar_for
from ui.views import content_for
from ui.app_config import TABS_ORDER as TABS, TAB_LABELS
from ui.utils import initialize_symbols


# ────────────────────────────────
# Configuración inicial
# ────────────────────────────────
st.set_page_config(page_title="Analizador Bursátil", layout="wide")

st.title("📈 Analizador Bursátil")

# ────────────────────────────────
# Tabs principales
# ────────────────────────────────
if "active_tab" not in st.session_state:
    st.session_state.active_tab = TABS[0]

selected_tab = st.radio(
    "Secciones",
    options=TABS,
    index=TABS.index(st.session_state.active_tab),
    horizontal=True,
    label_visibility="collapsed",
)

if selected_tab != st.session_state.active_tab:
    # CRÍTICO: Guardar valores ANTES del rerun (se pierden si no hay widget renderizado)
    temp_datos = st.session_state.get("datos_simbolos", "")
    temp_cartera = st.session_state.get("cartera_symbols", "")
    temp_weights = st.session_state.get("cartera_weights", "")
    
    st.session_state.active_tab = selected_tab
    
    # Restaurar valores explícitamente para que no se pierdan
    if temp_datos or temp_cartera or temp_weights:  # Solo si hay valores
        st.session_state["datos_simbolos"] = temp_datos
        st.session_state["cartera_symbols"] = temp_cartera
        st.session_state["cartera_weights"] = temp_weights
    
    st.rerun()

tab = st.session_state.active_tab

initialize_symbols()

# ────────────────────────────────
# Sidebar dinámico (dispatcher)
# ────────────────────────────────
submit, params = sidebar_for(tab)

# ────────────────────────────────
# Contenido central (dispatcher)
# ────────────────────────────────
content_for(tab, submit, params)
