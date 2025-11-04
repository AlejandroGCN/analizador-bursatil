from __future__ import annotations

import pandas as pd
import streamlit as st
from data_extractor import DataExtractor, ExtractorConfig
from ui.app_config import build_cfg_and_kind


@st.cache_resource(show_spinner=False)
def get_extractor(cfg_dict: dict, _cache_version: str = "v2") -> DataExtractor:
    """Crea y cachea el DataExtractor (todas las fuentes son públicas)."""
    cfg = ExtractorConfig(**cfg_dict)
    return DataExtractor(cfg)


def get_backend_params():
    """Obtiene los parámetros del sidebar para el backend."""
    fuente = st.session_state.get("fuente_datos")
    tipo = st.session_state.get("tipo_datos")
    interval = st.session_state.get("intervalo_datos")
    symbols = st.session_state.get("simbolos_datos")

    # Fechas de inicio y fin → convertir a Timestamp
    start = st.session_state.get("fecha_ini_datos")
    end = st.session_state.get("fecha_fin_datos")
    start = pd.to_datetime(start) if start else None
    end = pd.to_datetime(end) if end else None

    cfg_dict, kind = build_cfg_and_kind(fuente, tipo)
    cfg_dict["interval"] = interval

    if isinstance(symbols, str):
        # Soporta tanto comas como espacios como separadores
        symbols = [s.strip() for s in symbols.replace(" ", ",").split(",") if s.strip()]
        
        # Validar formato de símbolos
        for symbol in symbols:
            if "." in symbol and not any(symbol.endswith(f".{ext}") for ext in ["US", "DE", "FR", "UK", "JP", "CA"]):
                st.warning(f"⚠️ Advertencia: '{symbol}' parece estar mal formateado. Usa comas para separar múltiples símbolos: 'MSFT, GOOGL'")

    return cfg_dict, symbols, start, end, interval, kind


@st.cache_data(ttl=300, show_spinner=False, max_entries=10)
def fetch_market_data(cfg_dict: dict,
                      symbols: list[str],
                      start: pd.Timestamp | None,
                      end: pd.Timestamp | None,
                      interval: str,
                      kind: str,
                      _cache_version: str = "v2"):
    """Descarga y normaliza datos según los parámetros seleccionados."""
    extractor = get_extractor(cfg_dict, _cache_version)
    data_map = extractor.get_market_data(
        tickers=symbols,
        start=start,
        end=end,
        interval=interval,
        kind=kind,
    )
    
    # Convertir a formato serializable para el cache
    serializable_data = {}
    for symbol, series_obj in data_map.items():
        # Extraer el DataFrame del objeto series
        df = getattr(series_obj, "data", series_obj)
        serializable_data[symbol] = {
            "data": df,
            "type": type(series_obj).__name__,
            "kind": kind
        }
    
    return serializable_data
