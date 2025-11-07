# src/ui/dashboard.py
import os, sys
THIS_DIR = os.path.dirname(__file__)
SRC_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

import streamlit as st
import logging
import logging.config
import logging.handlers
import os
from pathlib import Path
from logs.logs_handler import resolve_log_cfg

# ───────────────────────────────────────────────────────────────
# 🔧 Funciones auxiliares para configuración de logging
# ───────────────────────────────────────────────────────────────


def _adjust_log_paths(cfg: dict, project_root: Path) -> None:
    """Ajusta los paths de handlers de logging a rutas absolutas."""
    for handler_cfg in cfg.get('handlers', {}).values():
        if isinstance(handler_cfg, dict) and 'filename' in handler_cfg:
            filename = handler_cfg['filename']
            if not os.path.isabs(filename):
                log_path = project_root / filename
                log_path.parent.mkdir(parents=True, exist_ok=True)
                handler_cfg['filename'] = str(log_path)


def _remove_debug_handler_from_config(cfg: dict) -> None:
    """Remueve el handler de debug de la configuración si está presente."""
    if 'debug_file' in cfg.get('handlers', {}):
        del cfg['handlers']['debug_file']
    
    for logger_cfg in cfg.get('loggers', {}).values():
        if isinstance(logger_cfg, dict) and 'handlers' in logger_cfg:
            logger_cfg['handlers'] = [
                h for h in logger_cfg['handlers'] if h != 'debug_file'
            ]


def _create_debug_handler(cfg: dict) -> logging.Handler | None:
    """Crea y configura el handler de debug si está disponible."""
    if 'debug_file' not in cfg.get('handlers', {}):
        return None
    
    debug_cfg = cfg['handlers']['debug_file']
    filename = debug_cfg.get('filename')
    
    if not filename or not Path(filename).parent.exists():
        return None
    
    handler = logging.handlers.RotatingFileHandler(
        filename=filename,
        maxBytes=debug_cfg.get('maxBytes', 10485760),
        backupCount=debug_cfg.get('backupCount', 3),
        encoding=debug_cfg.get('encoding', 'utf8')
    )
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        fmt=cfg['formatters']['detailed']['format'],
        datefmt=cfg['formatters']['detailed'].get('datefmt', '%Y-%m-%d %H:%M:%S')
    )
    handler.setFormatter(formatter)
    
    return handler


def _attach_debug_handler_to_loggers(handler: logging.Handler) -> None:
    """Añade el handler de debug a los loggers relevantes."""
    loggers_to_debug = ['ui', 'data_extractor', '']
    
    for logger_name in loggers_to_debug:
        logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)


def _setup_logging() -> None:
    """Configura el sistema de logging desde archivo YAML."""
    log_config_path = Path(__file__).parent.parent / "logs" / "logging.yaml"
    cfg_path = resolve_log_cfg(str(log_config_path))
    
    if not cfg_path:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return
    
    import yaml
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    
    project_root = Path(__file__).parent.parent.parent
    _adjust_log_paths(cfg, project_root)
    
    from ui.app_config import DEBUG_LOGGING_ENABLED
    
    if not DEBUG_LOGGING_ENABLED:
        _remove_debug_handler_from_config(cfg)
    
    logging.config.dictConfig(cfg)
    
    if DEBUG_LOGGING_ENABLED:
        debug_handler = _create_debug_handler(cfg)
        if debug_handler:
            _attach_debug_handler_to_loggers(debug_handler)
            logging.info("🔍 Debug logging activado. Logs detallados en var/logs/debug.log")


# ───────────────────────────────────────────────────────────────
# Configuración de logging
# ───────────────────────────────────────────────────────────────
_setup_logging()

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

# Inicializar símbolos solo una vez (optimización)
if "_symbols_initialized" not in st.session_state:
    initialize_symbols()
    st.session_state["_symbols_initialized"] = True

# Restaurar los valores guardados SOLO cuando cambia la pestaña
# (no en cada rerun para evitar sobrescribir lo que el usuario está escribiendo)
if st.session_state.get("_tab_change_occurred", False):
    saved_datos = st.session_state.get("saved_datos_simbolos", "")
    if saved_datos and saved_datos.strip():
        st.session_state["datos_simbolos"] = saved_datos

    saved_cartera_symbols = st.session_state.get("saved_cartera_symbols", "")
    if saved_cartera_symbols and saved_cartera_symbols.strip():
        st.session_state["cartera_symbols"] = saved_cartera_symbols

    saved_cartera_weights = st.session_state.get("saved_cartera_weights", "")
    if saved_cartera_weights and saved_cartera_weights.strip():
        st.session_state["cartera_weights"] = saved_cartera_weights
    
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
