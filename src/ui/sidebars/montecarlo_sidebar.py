from __future__ import annotations
from typing import Tuple
import streamlit as st
from .types import MonteCarloParams


def _get_available_symbols_for_individual_simulation() -> list[str]:
    """
    Obtiene los símbolos disponibles para simulación individual.
    
    Prioriza símbolos de la cartera configurada, luego todos los datos disponibles.
    
    Returns:
        Lista de símbolos disponibles para seleccionar
    """
    available_symbols = []
    
    # Primero intentar usar la cartera configurada
    if "portfolio_symbols" in st.session_state and st.session_state["portfolio_symbols"]:
        portfolio_symbols = st.session_state["portfolio_symbols"]
        # Verificar que los símbolos de la cartera estén en los datos descargados
        if "last_data_map" in st.session_state and st.session_state["last_data_map"]:
            data_map = st.session_state["last_data_map"]
            # Filtrar solo los símbolos de la cartera que están en los datos
            available_symbols = [
                symbol for symbol in portfolio_symbols 
                if symbol in data_map
            ]
    
    # Si no hay cartera o los símbolos no están en los datos, usar todos los datos disponibles
    if not available_symbols and "last_data_map" in st.session_state and st.session_state["last_data_map"]:
        data_map = st.session_state["last_data_map"]
        # Extraer símbolos del data_map
        available_symbols = list(data_map.keys())
        # Filtrar símbolos vacíos o inválidos
        available_symbols = [s for s in available_symbols if s and isinstance(s, str)]
    
    return available_symbols


def _render_symbol_selector_for_individual(available_symbols: list[str]) -> str:
    """
    Renderiza el selector de símbolo para simulación individual.
    
    Args:
        available_symbols: Lista de símbolos disponibles
    
    Returns:
        Símbolo seleccionado (cadena vacía si no hay símbolos disponibles)
    """
    if available_symbols:
        # Obtener el valor actual si ya existe
        current_symbol = st.session_state.get("mc_symbol_individual", available_symbols[0])
        # Asegurar que el símbolo actual esté en la lista
        if current_symbol not in available_symbols:
            current_symbol = available_symbols[0]
        
        return st.sidebar.selectbox(
            "Seleccionar activo",
            options=available_symbols,
            index=available_symbols.index(current_symbol) if current_symbol in available_symbols else 0,
            key="mc_symbol_individual",
            help="Elige el activo que quieres simular individualmente"
        )
    else:
        # Mostrar mensajes informativos según el caso
        if "portfolio_symbols" not in st.session_state or not st.session_state.get("portfolio_symbols"):
            st.sidebar.warning("⚠️ Primero configura una cartera en la pestaña '💼 Cartera' y descarga datos en '📊 Datos'.")
        elif "last_data_map" not in st.session_state or not st.session_state.get("last_data_map"):
            st.sidebar.warning("⚠️ Primero descarga datos en la pestaña '📊 Datos' para poder seleccionar un activo.")
        else:
            st.sidebar.warning("⚠️ Los símbolos de tu cartera no están disponibles en los datos descargados.")
        st.sidebar.info("💡 Configura la cartera y descarga datos para poder seleccionar un activo.")
        return ""


def sidebar_montecarlo() -> Tuple[bool, MonteCarloParams]:
    """Sidebar para la simulación Monte Carlo con opción de cartera o individual."""
    # Obtener valor inicial de la cartera configurada (si existe)
    valor_inicial_cartera = st.session_state.get("portfolio_valor_inicial", 10000.0)
    
    st.sidebar.header("🎲 Parámetros Monte Carlo")
    
    # Selector de tipo de simulación FUERA del form para que se actualice inmediatamente
    current_tipo = st.session_state.get("mc_tipo_simulacion", "cartera")
    
    tipo_simulacion = st.sidebar.radio(
        "Tipo de simulación",
        options=["cartera", "individual"],
        format_func=lambda x: "💼 Cartera completa" if x == "cartera" else "📊 Activo individual",
        key="mc_tipo_simulacion",
        index=0 if current_tipo == "cartera" else 1
    )
    
    st.sidebar.markdown("---")
    
    # Si es simulación individual, mostrar selector de símbolo FUERA del form
    symbol_individual = ""
    if tipo_simulacion == "individual":
        available_symbols = _get_available_symbols_for_individual_simulation()
        symbol_individual = _render_symbol_selector_for_individual(available_symbols)
    else:
        # Mostrar info del valor inicial de la cartera solo si es simulación de cartera
        if "portfolio_valor_inicial" in st.session_state:
            st.sidebar.info(f"💰 Valor inicial: ${valor_inicial_cartera:,.2f} (de cartera configurada)")
        else:
            st.sidebar.info("💰 Usando valor por defecto: $10,000.00")
    
    st.sidebar.markdown("---")
    
    # Resto de parámetros dentro del form
    with st.sidebar.form("form_montecarlo"):
        nsims = st.number_input(
            "Nº de simulaciones", 
            100, 
            10_000, 
            1000, 
            key="mc_nsims",
            help="Número de trayectorias aleatorias a simular. Más simulaciones = mayor precisión pero más tiempo."
        )
        horizonte = st.number_input(
            "Horizonte (días)", 
            1, 
            1260,  # Máximo: 5 años (252 días × 5 = 1260)
            252, 
            key="mc_horizonte",
            help="Días de trading a proyectar. 252 días = 1 año | 504 = 2 años | 1260 = 5 años"
        )
        vol_dyn = st.checkbox(
            "¿Volatilidad dinámica?", 
            key="mc_vol_dyn",
            help="Simula variaciones en la volatilidad (más realista pero menos predecible)."
        )
        
        submitted = st.form_submit_button(
            "💼 Lanzar simulación (Cartera)" if tipo_simulacion == "cartera" 
            else "📊 Lanzar simulación (Individual)",
            width='stretch'
        )
        
        # Validar que si es individual, haya un símbolo seleccionado
        if submitted and tipo_simulacion == "individual" and not symbol_individual:
            st.error("⚠️ Debes seleccionar un activo para simulación individual")
            submitted = False
    
    # Usar el valor de la cartera para cartera completa, o None para individual (se usará precio actual)
    valor_inicial = float(valor_inicial_cartera) if tipo_simulacion == "cartera" else 0.0
    
    return submitted, MonteCarloParams(
        int(nsims), 
        int(horizonte), 
        bool(vol_dyn), 
        valor_inicial,
        str(tipo_simulacion),
        str(symbol_individual) if symbol_individual else ""
    )
