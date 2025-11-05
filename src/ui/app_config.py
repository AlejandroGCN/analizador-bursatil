"""
Configuración central de la aplicación Streamlit.

Este módulo contiene toda la configuración de la interfaz de usuario,
incluyendo pestañas, fuentes de datos, tipos de series y configuración
de logging de depuración.
"""
from __future__ import annotations
from typing import Dict, List

# ───────────────────────────────────────────────────────────────
# 🎛️ Configuración general de la aplicación
# ───────────────────────────────────────────────────────────────

TAB_LABELS: Dict[str, str] = {
    "datos": "📊 Datos",
    "cartera": "💼 Cartera",
    "montecarlo": "🎲 Monte Carlo",
    "reporte": "📋 Reporte",
}
"""Mapeo de identificadores internos a etiquetas visibles de pestañas."""

TABS_ORDER: List[str] = [
    TAB_LABELS["datos"],
    TAB_LABELS["cartera"],
    TAB_LABELS["montecarlo"],
    TAB_LABELS["reporte"],
]
"""Orden de aparición de las pestañas en la interfaz."""

# Fuentes disponibles (dinámicamente detectadas)
def get_available_sources() -> Dict[str, str]:
    """
    Obtiene las fuentes de datos disponibles dinámicamente.
    
    Detecta automáticamente qué fuentes están disponibles en el sistema,
    incluyendo verificación de dependencias para Tiingo.
    
    Returns:
        Diccionario con nombre de fuente (UI) -> identificador interno
        
    Example:
        >>> sources = get_available_sources()
        >>> print(sources)
        {'Yahoo': 'yahoo', 'Binance': 'binance', 'Tiingo': 'tiingo'}
    """
    sources = {
        "Yahoo": "yahoo",
        "Binance": "binance",
    }
    
    # Intentar añadir Tiingo si está disponible
    try:
        from data_extractor.core.registry import TIINGO_AVAILABLE
        if TIINGO_AVAILABLE:
            sources["Tiingo"] = "tiingo"
    except ImportError:
        pass
    
    return sources

SOURCE_MAP = get_available_sources()
"""Mapeo de fuentes disponibles (actualizado dinámicamente)."""

KIND_MAP: Dict[str, str] = {
    "Precios Históricos": "ohlcv",
    "Retornos": "returns_pct",
}
"""Mapeo de tipos de series (UI) a identificadores internos."""

ALLOWED_INTERVALS = ["1d", "1h", "1wk"]
"""Intervalos temporales permitidos en la UI."""

ALLOWED_KINDS = list(KIND_MAP.keys())
"""Tipos de series permitidos en la UI."""

# ───────────────────────────────────────────────────────────────
# 🔍 Configuración de Logging Debug
# ───────────────────────────────────────────────────────────────

# Cambiar a True para activar logs de debug detallados
# Los logs se escribirán en var/logs/debug.log
DEBUG_LOGGING_ENABLED = True  # Activado para análisis de datos


def build_cfg_and_kind(fuente_human: str, tipo_human: str, intervalo: str = "1d") -> tuple[dict, str]:
    """
    Construye configuración del extractor a partir de etiquetas de la UI.
    
    Traduce las etiquetas legibles por humanos de la interfaz a los
    identificadores internos que espera el DataExtractor, y configura
    las API keys necesarias.
    
    Args:
        fuente_human: Nombre de la fuente en la UI (ej: "Yahoo", "Binance")
        tipo_human: Tipo de serie en la UI (ej: "Precios Históricos")
        intervalo: Intervalo temporal (ej: "1d", "1h", "1wk")
    
    Returns:
        Tupla con (diccionario de configuración, tipo de serie interno)
        
    Example:
        >>> cfg, kind = build_cfg_and_kind("Yahoo", "Precios Históricos", "1d")
        >>> print(cfg)
        {'source': 'yahoo', 'interval': '1d'}
        >>> print(kind)
        'ohlcv'
    
    Note:
        Para Tiingo, automáticamente carga la API key desde el archivo .env
        si está disponible.
    """
    import os
    from pathlib import Path
    from dotenv import load_dotenv
    
    source = SOURCE_MAP.get(fuente_human, "yahoo")
    kind = KIND_MAP.get(tipo_human, "ohlcv")
    cfg_dict = {"source": source, "interval": intervalo}
    
    # Para Tiingo, obtener API key de variables de entorno
    if source == "tiingo":
        # Asegurarse de que .env está cargado
        env_file = Path(__file__).parent.parent.parent / ".env"
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=False)
        
        api_key = os.getenv("TIINGO_API_KEY")
        if api_key:
            cfg_dict["api_key"] = api_key
    
    return cfg_dict, kind
