"""Sidebars por pestaña del analizador bursátil."""
from __future__ import annotations
from typing import Tuple, Any, Dict, Callable
from ui.app_config import TAB_LABELS
from .types import DatosParams, CarteraParams, MonteCarloParams, ReporteParams

# Importar funciones de sidebars
from .datos_sidebar import sidebar_datos
from .cartera_sidebar import sidebar_cartera
from .montecarlo_sidebar import sidebar_montecarlo
from .reporte_sidebar import sidebar_reporte

# Dispatcher
TAB_TO_SIDEBAR: Dict[str, Callable[[], Tuple[bool, Any]]] = {
    TAB_LABELS["datos"]: sidebar_datos,
    TAB_LABELS["cartera"]: sidebar_cartera,
    TAB_LABELS["montecarlo"]: sidebar_montecarlo,
    TAB_LABELS["reporte"]: sidebar_reporte,
}

def sidebar_for(tab: str) -> Tuple[bool, Any]:
    """Dispatchea al sidebar correspondiente según la pestaña."""
    fn = TAB_TO_SIDEBAR.get(tab)
    if fn is None:
        import streamlit as st
        st.sidebar.empty()
        return False, None
    return fn()

__all__ = ["sidebar_for", "DatosParams", "CarteraParams", "MonteCarloParams", "ReporteParams"]

