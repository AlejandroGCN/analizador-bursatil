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
    "config": "⚙️ Configuración",
}

TABS_ORDER: List[str] = [
    TAB_LABELS["datos"],
    TAB_LABELS["cartera"],
    TAB_LABELS["montecarlo"],
    TAB_LABELS["reporte"],
    TAB_LABELS["config"],
]

# Fuentes disponibles
SOURCE_MAP: Dict[str, str] = {
    "Yahoo": "yahoo",
    "Binance": "binance",
    "Stooq": "stooq",
}

KIND_MAP: Dict[str, str] = {
    "Precios Históricos": "ohlcv",
    "Retornos": "returns_pct",
}

ALLOWED_INTERVALS = ["1d", "1h", "1wk"]
ALLOWED_KINDS = list(KIND_MAP.keys())


def build_cfg_and_kind(fuente_human: str, tipo_human: str, intervalo: str) -> tuple[dict, str]:
    """Traduce labels de la UI a claves internas y construye cfg_dict + kind."""
    source = SOURCE_MAP.get(fuente_human, "yahoo")
    kind = KIND_MAP.get(tipo_human, "ohlcv")
    cfg_dict = {"source": source, "interval": intervalo}
    return cfg_dict, kind
