from __future__ import annotations
from typing import Tuple
import streamlit as st
from .types import MonteCarloParams


def sidebar_montecarlo() -> Tuple[bool, MonteCarloParams]:
    # Obtener valor inicial de la cartera configurada (si existe)
    valor_inicial_cartera = st.session_state.get("portfolio_valor_inicial", 10000.0)
    
    with st.sidebar.form("form_montecarlo"):
        st.header("🎲 Parámetros Monte Carlo")
        
        # Mostrar info del valor inicial de la cartera
        if "portfolio_valor_inicial" in st.session_state:
            st.info(f"💰 Valor inicial: ${valor_inicial_cartera:,.2f} (de cartera configurada)")
        else:
            st.info("💰 Usando valor por defecto: $10,000.00")
        
        nsims = st.number_input("Nº de simulaciones", 100, 10_000, 1000, key="mc_nsims")
        horizonte = st.number_input("Horizonte (días)", 1, 365, 252, key="mc_horizonte")
        vol_dyn = st.checkbox("¿Volatilidad dinámica?", key="mc_vol_dyn")
        submitted = st.form_submit_button("Lanzar simulación")
    
    # Usar el valor de la cartera (no un input separado)
    return submitted, MonteCarloParams(int(nsims), int(horizonte), bool(vol_dyn), float(valor_inicial_cartera))

