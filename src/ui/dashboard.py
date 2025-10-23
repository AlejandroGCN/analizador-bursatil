# src/ui/dashboard.py
import os, sys
THIS_DIR = os.path.dirname(__file__)
SRC_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

import streamlit as st

# ── imports principales ───────────────────────────────────────────────
from ui.sidebars import sidebar_for
from ui.views import content_for
from ui.app_config import TABS_ORDER as TABS


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
    st.session_state.active_tab = selected_tab
    st.rerun()

tab = st.session_state.active_tab

# ────────────────────────────────
# Sidebar dinámico (dispatcher)
# ────────────────────────────────
submit, params = sidebar_for(tab)

# ────────────────────────────────
# Contenido central (dispatcher)
# ────────────────────────────────
content_for(tab, submit, params)
