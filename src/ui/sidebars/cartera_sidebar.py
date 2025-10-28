from __future__ import annotations
from typing import Tuple
import streamlit as st
import pandas as pd
from .types import CarteraParams
from ui.utils import (
    validate_and_clean_symbols,
    apply_sidebar_styles,
    render_symbol_import_controls,
    render_file_upload_controls
)


def _cleanup_old_weights() -> None:
    """Limpia los pesos de símbolos antiguos de session_state."""
    keys_to_delete = [key for key in st.session_state.keys() if key.startswith("weight_")]
    for key in keys_to_delete:
        del st.session_state[key]


def _calculate_equal_weights(n_symbols: int) -> list[float]:
    """Calcula pesos iguales para todos los símbolos que suman exactamente 1.0."""
    base_weight = 1.0 / n_symbols
    weights = [base_weight] * n_symbols
    total = sum(weights)
    if total < 1.0:
        adjustment = 1.0 - total
        weights[0] += adjustment
    return weights


def _render_weight_inputs(symbols_list: list[str]) -> None:
    """Renderiza los inputs de pesos para cada símbolo."""
    if not symbols_list:
        return
    
    st.markdown("---")
    st.markdown("**Asigna pesos a cada activo (en %):**")
    
    n = len(symbols_list)
    base_pct = round(100.0 / n)
    adjustment = 100 - (base_pct * n)
    
    for i, symbol in enumerate(symbols_list):
        weight_key = f"weight_{symbol}"
        default_value = base_pct + adjustment if i == 0 else base_pct
        
        if weight_key not in st.session_state:
            st.session_state[weight_key] = default_value
        
        st.number_input(
            symbol,
            min_value=0,
            max_value=100,
            step=1,
            key=weight_key,
            help="%"
        )


def _validate_symbols_on_submit(symbols_input: str) -> tuple[list[str], list[str]]:
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


def _process_and_validate_weights(validated_symbols: list[str]) -> str:
    """Procesa y valida los pesos ingresados."""
    if not validated_symbols:
        return "1.0"
    
    weights_inputs = []
    for symbol in validated_symbols:
        weight_key = f"weight_{symbol}"
        percent_value = st.session_state.get(weight_key, 0)
        weight = percent_value / 100.0
        weights_inputs.append(weight)
    
    total_weight = sum(weights_inputs)
    
    if 0.98 <= total_weight <= 1.02:
        st.success(f"✅ Total: {total_weight:.1%}")
        return ",".join([str(w) for w in weights_inputs])
    elif total_weight == 0:
        st.info("💡 Suma 0%. Se usarán pesos iguales.")
        equal_weight = 1.0 / len(validated_symbols)
        equal_weights = [equal_weight] * len(validated_symbols)
        return ",".join([str(w) for w in equal_weights])
    elif total_weight > 1.02:
        st.error(f"❌ Total: {total_weight:.1%} - Los pesos suman más del 100%. Corrígelos antes de continuar.")
        return ""
    else:  # total_weight < 0.98
        st.warning(f"⚠️ Total: {total_weight:.1%} (suma menos de 100%)")
        normalized = [w / total_weight for w in weights_inputs]
        return ",".join([str(w) for w in normalized])


def _update_weights_if_symbols_changed():
    """Recalcula pesos automáticamente cuando cambian los símbolos."""
    current_symbols = st.session_state.get("cartera_symbols", "")
    if not current_symbols:
        return
    
    new_symbols_list = [s.strip() for s in current_symbols.split(",") if s.strip()]
    old_symbols = st.session_state.get("portfolio_symbols", [])
    
    # Limpiar cartera guardada si los símbolos cambian
    if old_symbols and new_symbols_list != old_symbols:
        if "portfolio_symbols" in st.session_state:
            del st.session_state["portfolio_symbols"]
        if "portfolio_weights" in st.session_state:
            del st.session_state["portfolio_weights"]
    
    # Recalcular pesos
    if new_symbols_list:
        _cleanup_old_weights()
        weights = _calculate_equal_weights(len(new_symbols_list))
        weights_str = ",".join([str(round(w * 100)) for w in weights])
        st.session_state.cartera_weights = weights_str


def sidebar_cartera() -> Tuple[bool, CarteraParams]:
    """Sidebar para la pestaña de Cartera."""
    st.sidebar.header("💼 Parámetros de cartera")
    
    # Aplicar estilos del sidebar (función reutilizable)
    apply_sidebar_styles()
    
    # Controles de importación de símbolos (función reutilizable)
    render_symbol_import_controls(
        source_key="datos_simbolos",
        target_key="cartera_symbols",
        from_label="Datos",
        button_label="📊 Importar símbolos desde Datos"
    )
    
    # Controles de carga de archivos (función reutilizable)
    render_file_upload_controls(
        target_key="cartera_symbols",
        button_label="📁 Cargar símbolos desde archivo",
        uploader_key="file_uploader_cartera"
    )
    
    st.sidebar.markdown("---")
    
    # Actualizar pesos automáticamente si cambian los símbolos
    _update_weights_if_symbols_changed()
    
    # Obtener símbolos para usarlos en el form
    symbols_input = st.session_state.get("cartera_symbols", "")
    symbols_list = [s.strip() for s in symbols_input.split(",") if s.strip()] if symbols_input else []
    
    # Formulario
    with st.sidebar.form("form_cartera"):
        valor_inicial_input = st.number_input(
            "💰 Valor inicial de la cartera ($)", 100.0, 1_000_000.0, 10000.0, step=1000.0, key="cartera_valor_inicial"
        )
        
        # Renderizar inputs de pesos usando función auxiliar
        _render_weight_inputs(symbols_list)
        
        submitted = st.form_submit_button(
            "💼 Aplicar pesos",
            width='stretch'
        )
    
    # Validar símbolos y procesar pesos si se envió el formulario
    weights_str_final = "1.0"
    if submitted:
        valid_symbols, _ = _validate_symbols_on_submit(symbols_input)
        if valid_symbols:
            weights_str_final = _process_and_validate_weights(valid_symbols) or "1.0"
    
    # NO guardar symbols_input en session_state porque el input ya lo hace automáticamente
    # al tener key="cartera_symbols"
    
    return submitted, CarteraParams(symbols_input, weights_str_final, float(valor_inicial_input))

