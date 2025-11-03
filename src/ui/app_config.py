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

TABS_ORDER: List[str] = [
    TAB_LABELS["datos"],
    TAB_LABELS["cartera"],
    TAB_LABELS["montecarlo"],
    TAB_LABELS["reporte"],
]

# Fuentes disponibles (dinámicamente detectadas)
def get_available_sources() -> Dict[str, str]:
    """Obtiene las fuentes disponibles dinámicamente."""
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

KIND_MAP: Dict[str, str] = {
    "Precios Históricos": "ohlcv",
    "Retornos": "returns_pct",
}

ALLOWED_INTERVALS = ["1d", "1h", "1wk"]
ALLOWED_KINDS = list(KIND_MAP.keys())

# ───────────────────────────────────────────────────────────────
# 🔍 Configuración de Logging Debug
# ───────────────────────────────────────────────────────────────

# Cambiar a True para activar logs de debug detallados
# Los logs se escribirán en var/logs/debug.log
DEBUG_LOGGING_ENABLED = True  # Activado para análisis de datos


def build_cfg_and_kind(fuente_human: str, tipo_human: str, intervalo: str = "1d") -> tuple[dict, str]:
    """Traduce labels de la UI a claves internas y construye cfg_dict + kind."""
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
