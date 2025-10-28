# src/ui/dashboard.py
import os, sys
THIS_DIR = os.path.dirname(__file__)
SRC_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

import streamlit as st
import logging
import os
from pathlib import Path
from logs.logs_handler import resolve_log_cfg

# Configurar logging desde archivo YAML con paths ajustados
log_config_path = Path(__file__).parent.parent / "logs" / "logging.yaml"
cfg_path = resolve_log_cfg(str(log_config_path))

if cfg_path:
    import yaml
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    
    # Ajustar paths de handlers a la raíz del proyecto
    project_root = Path(__file__).parent.parent.parent
    for handler_name, handler_cfg in cfg.get('handlers', {}).items():
        if isinstance(handler_cfg, dict) and 'filename' in handler_cfg:
            filename = handler_cfg['filename']
            if not os.path.isabs(filename):
                log_dir = project_root / filename
                log_dir.parent.mkdir(parents=True, exist_ok=True)
                handler_cfg['filename'] = str(log_dir)
    
    # Aplicar configuración
    import logging.config
    logging.config.dictConfig(cfg)
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

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

# Guardar valores de la pestaña ACTUAL antes de cambiar
current_tab = st.session_state.active_tab

if selected_tab != current_tab:
    # Guardar los valores actuales SOLO si no están vacíos
    # Esto evita sobrescribir valores guardados con cadenas vacías cuando
    # los widgets no se han renderizado en la pestaña actual
    current_datos = st.session_state.get("datos_simbolos", "")
    current_cartera = st.session_state.get("cartera_symbols", "")
    current_weights = st.session_state.get("cartera_weights", "")
    
    # Solo actualizar saved_* si el valor actual no está vacío
    # Esto preserva los valores guardados anteriores
    if current_datos and current_datos.strip():
        st.session_state["saved_datos_simbolos"] = current_datos
    if current_cartera and current_cartera.strip():
        st.session_state["saved_cartera_symbols"] = current_cartera
    if current_weights and current_weights.strip():
        st.session_state["saved_cartera_weights"] = current_weights
    
    # Marcar que vamos a cambiar de pestaña para restaurar valores en el próximo render
    st.session_state["_tab_change_occurred"] = True
    st.session_state.active_tab = selected_tab
    st.rerun()

tab = st.session_state.active_tab

initialize_symbols()

# Restaurar los valores guardados SOLO cuando cambia la pestaña
# (no en cada rerun para evitar sobrescribir lo que el usuario está escribiendo)
if st.session_state.get("_tab_change_occurred", False):
    if "saved_datos_simbolos" in st.session_state:
        st.session_state["datos_simbolos"] = st.session_state["saved_datos_simbolos"]
    if "saved_cartera_symbols" in st.session_state:
        st.session_state["cartera_symbols"] = st.session_state["saved_cartera_symbols"]
    if "saved_cartera_weights" in st.session_state:
        st.session_state["cartera_weights"] = st.session_state["saved_cartera_weights"]
    
    # Limpiar la bandera para que no se ejecute en siguientes renders
    st.session_state["_tab_change_occurred"] = False

# ────────────────────────────────
# Sidebar dinámico (dispatcher)
# ────────────────────────────────
submit, params = sidebar_for(tab)

# ────────────────────────────────
# Contenido central (dispatcher)
# ────────────────────────────────
content_for(tab, submit, params)
