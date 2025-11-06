from __future__ import annotations
from typing import Tuple
import streamlit as st
import pandas as pd
import logging
from .types import CarteraParams
from ui.utils import (
    validate_and_clean_symbols,
    apply_sidebar_styles,
    render_symbol_import_controls,
    render_file_upload_controls
)

logger = logging.getLogger(__name__)

# Rutas de archivos para persistencia
PORTFOLIO_CONFIG_PATH = "var/config/portfolio.json"

# Constantes
MIN_CAPITAL_PER_STOCK = 100.0
DEFAULT_INITIAL_VALUE = 10000.0
LAST_SYMBOLS_PROCESSED_KEY = "_last_symbols_processed"


def _save_portfolio_config(symbols: list[str], weights: list[float], initial_value: float) -> None:
    """Guarda la configuración de la cartera en un archivo JSON."""
    import json
    import os
    
    config = {
        "symbols": symbols,
        "weights": weights,
        "valor_inicial": initial_value,
        "timestamp": pd.Timestamp.now().isoformat()
    }
    
    os.makedirs(os.path.dirname(PORTFOLIO_CONFIG_PATH), exist_ok=True)
    
    with open(PORTFOLIO_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"💾 Configuración guardada en {PORTFOLIO_CONFIG_PATH}")


def _remove_orphaned_weights(active_symbols: list[str]) -> None:
    """Elimina los pesos de símbolos que ya no están en la lista activa."""
    active_keys = {f"weight_{s}" for s in active_symbols}
    orphaned_keys = [
        key for key in st.session_state.keys()
        if key.startswith("weight_") and key not in active_keys
    ]
    
    if orphaned_keys:
        logger.info(f"🗑️ Eliminando {len(orphaned_keys)} pesos huérfanos")
        for key in orphaned_keys:
            del st.session_state[key]


def _convert_to_percentage_weights(fractions: list[float]) -> list[int]:
    """
    Convierte fracciones a porcentajes enteros que suman exactamente 100%.
    Distribuye el residuo de forma determinista a los valores con mayor parte decimal.
    """
    raw_percentages = [f * 100.0 for f in fractions]
    floor_percentages = [int(p) for p in raw_percentages]
    remainder = 100 - sum(floor_percentages)
    
    # Asignar el residuo a los valores con mayor parte decimal
    decimal_parts = sorted(
        enumerate([r - f for r, f in zip(raw_percentages, floor_percentages)]),
        key=lambda x: x[1],
        reverse=True
    )
    
    for idx, _ in decimal_parts[:remainder]:
        floor_percentages[idx] += 1
    
    return floor_percentages


def _calculate_equal_weights(n_symbols: int) -> list[float]:
    """Calcula pesos iguales para todos los símbolos que suman exactamente 1.0."""
    base_percent = 100 // n_symbols
    remainder = 100 % n_symbols
    
    weights = []
    for i in range(n_symbols):
        percent = base_percent + (1 if i < remainder else 0)
        weights.append(percent / 100.0)
    
    return weights


def _normalize_weights(weights: list[float]) -> list[float]:
    """Normaliza los pesos para que sumen exactamente 1.0."""
    total = sum(weights)
    if total > 0:
        return [w / total for w in weights]
    return weights


def _render_weight_inputs(symbols_list: list[str]) -> None:
    """Renderiza los inputs de pesos para cada símbolo."""
    if not symbols_list:
        return
    
    st.markdown("---")
    st.markdown("**Asigna pesos a cada activo (en %):**")
    
    initial_value = st.session_state.get("cartera_valor_inicial", DEFAULT_INITIAL_VALUE)
    n = len(symbols_list)
    base_pct = 100 // n
    remainder = 100 % n
    
    for i, symbol in enumerate(symbols_list):
        weight_key = f"weight_{symbol}"
        default_value = base_pct + (1 if i < remainder else 0)
        
        if weight_key not in st.session_state:
            st.session_state[weight_key] = default_value
        
        weight_pct = st.session_state.get(weight_key, default_value)
        capital = (weight_pct / 100.0) * initial_value
        
        st.number_input(
            symbol,
            min_value=0,
            max_value=100,
            step=1,
            key=weight_key,
            help=f"Capital asignado: ${capital:,.2f}"
        )


def _validate_symbols_input(symbols_input: str) -> tuple[list[str], list[str]]:
    """Valida los símbolos cuando se envía el formulario."""
    if not symbols_input or not symbols_input.strip():
        st.error("❌ Debes ingresar al menos un símbolo para configurar la cartera.")
        return [], []
    
    valid_symbols, invalid_symbols = validate_and_clean_symbols(symbols_input)
    
    if invalid_symbols:
        st.warning("⚠️ Símbolos inválidos detectados:\n- " + "\n- ".join(invalid_symbols))
        st.info("💡 Los símbolos válidos son los que se usarán.")
    
    if not valid_symbols and invalid_symbols:
        st.error("❌ No se encontraron símbolos válidos. Verifica el formato (ej: AAPL, MSFT, GOOGL)")
    
    return valid_symbols, invalid_symbols


def _sync_weights_with_symbols() -> None:
    """Actualiza automáticamente los pesos cuando cambian los símbolos."""
    current_symbols = st.session_state.get("cartera_symbols", "")
    if not current_symbols:
        return
    
    new_symbols_list = [s.strip() for s in current_symbols.split(",") if s.strip()]
    last_symbols = st.session_state.get(LAST_SYMBOLS_PROCESSED_KEY, [])
    
    if new_symbols_list != last_symbols:
        logger.info(f"Detectado cambio de símbolos: {last_symbols} -> {new_symbols_list}")
        
        _remove_orphaned_weights(new_symbols_list)
        
        weights = _calculate_equal_weights(len(new_symbols_list))
        
        for i, symbol in enumerate(new_symbols_list):
            weight_key = f"weight_{symbol}"
            st.session_state[weight_key] = round(weights[i] * 100)
        
        st.session_state[LAST_SYMBOLS_PROCESSED_KEY] = new_symbols_list


def _ensure_weights_initialized(symbols_list: list[str]) -> None:
    """Asegura que todos los símbolos tengan pesos inicializados."""
    missing_weights = [
        symbol for symbol in symbols_list 
        if f"weight_{symbol}" not in st.session_state
    ]
    
    if missing_weights:
        logger.info(f"Inicializando pesos faltantes para: {missing_weights}")
        weights = _calculate_equal_weights(len(symbols_list))
        for i, symbol in enumerate(symbols_list):
            weight_key = f"weight_{symbol}"
            if weight_key not in st.session_state:
                st.session_state[weight_key] = round(weights[i] * 100)


def _collect_weights_from_session(symbols_list: list[str]) -> list[float]:
    """Recolecta los pesos desde session_state y los convierte a fracciones."""
    weights = []
    for symbol in symbols_list:
        weight_key = f"weight_{symbol}"
        weight_percent = st.session_state.get(weight_key, 0)
        weights.append(weight_percent / 100.0)
    return weights


def _validate_weights_sum(symbols_list: list[str]) -> Tuple[list[float], bool]:
    """
    Valida que los pesos sumen exactamente 100%.
    Retorna (pesos_como_fracciones, es_valido).
    
    NO normaliza automáticamente - el usuario DEBE ajustar manualmente.
    """
    weights = _collect_weights_from_session(symbols_list)
    total_weight = sum(weights)
    
    # Validar que sumen 100% (tolerancia del 1%)
    if total_weight == 0:
        st.error("❌ **Error:** Debes asignar pesos a los activos")
        return weights, False
    
    if abs(total_weight - 1.0) > 0.01:
        total_pct = total_weight * 100
        logger.info(f"Pesos no suman 100%: {total_pct:.1f}% (normalización automática, mostrado en UI)")
        
        # Mostrar error claro al usuario
        st.error(
            f"❌ **Los pesos deben sumar exactamente 100%**\n\n"
            f"📊 **Suma actual:** {total_pct:.1f}%\n\n"
            f"Por favor, ajusta los porcentajes en el panel lateral."
        )
        return weights, False
    
    return weights, True


def _validate_capital_per_stock(symbols_list: list[str], weights: list[float], initial_value: float) -> None:
    """Valida que cada activo tenga capital mínimo recomendado."""
    for i, symbol in enumerate(symbols_list):
        capital = weights[i] * initial_value
        if capital < MIN_CAPITAL_PER_STOCK:
            st.warning(
                f"⚠️ {symbol}: ${capital:.2f} es muy bajo para trading. "
                f"Mínimo recomendado: ${MIN_CAPITAL_PER_STOCK}"
            )


def sidebar_cartera() -> Tuple[bool, CarteraParams]:
    """Sidebar para la pestaña de Cartera."""
    st.sidebar.header("💼 Parámetros de cartera")
    
    apply_sidebar_styles()
    
    render_symbol_import_controls(
        source_key="datos_simbolos",
        target_key="cartera_symbols",
        from_label="Datos",
        button_label="📊 Importar símbolos desde Datos"
    )
    
    render_file_upload_controls(
        target_key="cartera_symbols",
        button_label="📁 Cargar símbolos desde archivo",
        uploader_key="file_uploader_cartera"
    )
    
    _sync_weights_with_symbols()
    
    with st.sidebar.form("form_cartera"):
        current_symbols = st.session_state.get("cartera_symbols", "")
        current_symbols_list = [
            s.strip() for s in current_symbols.split(",") if s.strip()
        ] if current_symbols else []
        
        st.markdown("💰 **Parámetros**")
        
        st.number_input(
            "Valor inicial de la cartera ($)",
            100.0,
            100_000_000.0,  # Límite: 100 millones (cubre individual + institucional)
            DEFAULT_INITIAL_VALUE,
            step=1000.0,
            key="cartera_valor_inicial",
            help="Capital inicial a invertir. Puede ir desde $100 hasta $100M."
        )
        
        if current_symbols_list:
            _render_weight_inputs(current_symbols_list)
        
        submitted = st.form_submit_button(
            "💼 Aplicar Pesos",
            width='stretch',
            disabled=not current_symbols_list
        )
    
    if submitted:
        submitted_symbols = st.session_state.get("cartera_symbols", "")
        symbols_list = [
            s.strip() for s in submitted_symbols.split(",") if s.strip()
        ] if submitted_symbols else []
        
        if not symbols_list:
            return False, CarteraParams("", "", DEFAULT_INITIAL_VALUE)
        
        _ensure_weights_initialized(symbols_list)
        valid_symbols, _ = _validate_symbols_input(submitted_symbols)
        
        if not valid_symbols:
            return False, CarteraParams("", "", DEFAULT_INITIAL_VALUE)
        
        # Validar que los pesos sumen 100%
        weights, is_valid = _validate_weights_sum(valid_symbols)
        
        # Si los pesos no suman 100%, NO continuar
        if not is_valid:
            return False, CarteraParams("", "", DEFAULT_INITIAL_VALUE)
        
        valor_inicial = st.session_state.get("cartera_valor_inicial", DEFAULT_INITIAL_VALUE)
        
        _save_portfolio_config(valid_symbols, weights, valor_inicial)
        _validate_capital_per_stock(valid_symbols, weights, valor_inicial)
        
        weights_str = ",".join([str(w) for w in weights])
        
        return True, CarteraParams(submitted_symbols, weights_str, float(valor_inicial))
    
    final_symbols = st.session_state.get("cartera_symbols", "")
    valor_inicial = st.session_state.get("cartera_valor_inicial", DEFAULT_INITIAL_VALUE)
    
    return False, CarteraParams(final_symbols, "", float(valor_inicial))
