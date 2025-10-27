"""Vistas por pestaña del analizador bursátil."""
from __future__ import annotations
from typing import Any, Dict, Callable
from ui.app_config import TAB_LABELS
from .datos_view import tab_datos
from .cartera_view import tab_cartera  
from .montecarlo_view import tab_montecarlo
from .reporte_view import tab_reporte


# Dispatcher
TAB_TO_VIEW: Dict[str, Callable[[bool, Any], None]] = {
    TAB_LABELS["datos"]: tab_datos,
    TAB_LABELS["cartera"]: tab_cartera,
    TAB_LABELS["montecarlo"]: tab_montecarlo,
    TAB_LABELS["reporte"]: tab_reporte,
}

def content_for(tab: str, submit: bool, params: Any) -> None:
    """
    Renderiza el contenido central para la pestaña indicada.
    Si no hay función asociada, no muestra nada.
    """
    fn = TAB_TO_VIEW.get(tab)
    if fn:
        fn(submit, params)

__all__ = ["tab_datos", "tab_cartera", "tab_montecarlo", "tab_reporte", "content_for"]
