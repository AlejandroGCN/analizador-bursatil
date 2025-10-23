# src/ui/services_backend.py
from __future__ import annotations
import pandas as pd
import streamlit as st
from data_extractor import DataExtractor, ExtractorConfig
from ui.app_config import build_cfg_and_kind

@st.cache_resource(show_spinner=False)
def get_extractor(cfg_dict: dict) -> DataExtractor:
    cfg = ExtractorConfig(**cfg_dict)
    return DataExtractor(cfg)

@st.cache_data(show_spinner=False, ttl=600)
def fetch_market_data(cfg_dict: dict,
                      symbols_csv: str,
                      start: pd.Timestamp | None,
                      end: pd.Timestamp | None,
                      interval: str,
                      kind: str):
    extractor = get_extractor(cfg_dict)
    symbols = [s.strip() for s in symbols_csv.split(",") if s.strip()]
    return extractor.get_market_data(
        tickers=symbols,
        start=start,
        end=end,
        interval=interval,
        kind=kind,
    )

def resolve_backend_params():
    """
    Lee parámetros de la UI desde session_state y retorna una tupla
    (cfg_dict, symbols, start, end, interval, kind), usando los mapas centralizados.
    """
    fuente_human = st.session_state.get("fuente_datos", "Yahoo")
    symbols = st.session_state.get("simbolos_datos", "AAPL,MSFT")
    start = st.session_state.get("fecha_ini_datos")
    end = st.session_state.get("fecha_fin_datos")
    interval = st.session_state.get("intervalo_datos", "1d")
    tipo_human = st.session_state.get("tipo_datos", "OHLCV")
    cfg_dict, kind = build_cfg_and_kind(fuente_human, tipo_human, interval)
    return cfg_dict, symbols, start, end, interval, kind
