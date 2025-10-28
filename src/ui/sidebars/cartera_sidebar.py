from __future__ import annotations
from typing import Tuple
import streamlit as st
import pandas as pd
from .types import CarteraParams


def sidebar_cartera() -> Tuple[bool, CarteraParams]:
    """Sidebar para la pestaña de Cartera."""
    st.sidebar.header("💼 Parámetros de cartera")
    
    # CSS para sidebar un poco más oscuro
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #d4e4f7;
    }
    [data-testid="stSidebar"] > div {
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Botón de importar desde datos (ANTES del widget)
    btn_import = st.sidebar.button("📊 Importar símbolos desde Datos", key="btn_import_cartera", width='stretch')
    
    if btn_import:
        datos_simbolos = st.session_state.get("datos_simbolos", "")
        if datos_simbolos and datos_simbolos.strip():
            st.session_state.cartera_symbols = datos_simbolos
            st.success("✅ Símbolos importados desde Datos")
        else:
            st.warning("⚠️ No hay símbolos en Datos")
    
    # Sección de carga de archivos
    uploaded_file = st.sidebar.file_uploader(
        "Selecciona un archivo",
        type=['csv', 'xlsx', 'xls', 'json', 'txt'],
        help="Formatos: CSV, Excel, JSON, TXT",
        key="file_uploader_cartera"
    )
    
    btn_load = st.sidebar.button("📁 Cargar símbolos desde archivo", key="btn_load_file_cartera", width='stretch')
    
    if btn_load and uploaded_file is not None:
        try:
            from ui.file_loader import load_symbols_from_file
            symbols = load_symbols_from_file(uploaded_file)
            if symbols:
                st.session_state.cartera_symbols = ",".join(symbols)
                st.success(f"✅ {len(symbols)} símbolos cargados")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    elif btn_load:
        st.warning("⚠️ Primero selecciona un archivo")
    
    st.sidebar.markdown("---")
    
    def _cleanup_old_weights() -> None:
        """
        Limpia los pesos de símbolos antiguos de session_state.
        
        Elimina todas las keys que empiezan con "weight_" para evitar
        conflictos cuando cambian los símbolos de la cartera.
        """
        keys_to_delete = []
        for key in st.session_state.keys():
            if key.startswith("weight_"):
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del st.session_state[key]
    
    # Calcular pesos automáticamente cuando cambian los símbolos
    current_symbols = st.session_state.get("cartera_symbols", "")
    if current_symbols:
        new_symbols_list = [s.strip() for s in current_symbols.split(",") if s.strip()]
        old_symbols = st.session_state.get("portfolio_symbols", [])
        
        # Si los símbolos cambian, limpiar la cartera guardada
        if old_symbols and new_symbols_list != old_symbols:
            if "portfolio_symbols" in st.session_state:
                del st.session_state["portfolio_symbols"]
            if "portfolio_weights" in st.session_state:
                del st.session_state["portfolio_weights"]
        
        # Recalcular pesos - ajustar para que sumen exactamente 100%
        if new_symbols_list:
            _cleanup_old_weights()
            n_symbols = len(new_symbols_list)
            base_weight = 1.0 / n_symbols
            
            # Calcular pesos base y ajuste
            weights = [base_weight] * n_symbols
            
            # Ajustar el primer peso para compensar errores de redondeo
            # Ejemplo: 3 activos -> 0.333... cada uno, sumaría 0.999, ajustamos a 0.334, 0.333, 0.333
            total = sum(weights)
            if total < 1.0:
                adjustment = 1.0 - total
                weights[0] += adjustment
            
            # Guardar como porcentajes
            weights_str = ",".join([str(round(w * 100)) for w in weights])
            st.session_state.cartera_weights = weights_str
    
    # Obtener símbolos para usarlos en el form
    symbols_input = st.session_state.get("cartera_symbols", "")
    symbols_list = [s.strip() for s in symbols_input.split(",") if s.strip()]
    
    # Formulario
    with st.sidebar.form("form_cartera"):
        valor_inicial_input = st.number_input(
            "💰 Valor inicial de la cartera ($)", 100.0, 1_000_000.0, 10000.0, step=1000.0, key="cartera_valor_inicial"
        )
        
        weights_str = ""
        
        if symbols_list:
            st.markdown("---")
            st.markdown("**Asigna pesos a cada activo (en %):**")
            
            # Mostrar inputs de pesos - ajustar para que sume 100%
            n = len(symbols_list)
            base_pct = round(100.0 / n)
            adjustment = 100 - (base_pct * n)  # Diferencia para llegar a 100
            
            for i, symbol in enumerate(symbols_list):
                weight_key = f"weight_{symbol}"
                # El primer símbolo recibe el ajuste para sumar exactamente 100%
                default_value = base_pct + adjustment if i == 0 else base_pct
                
                # Inicializar si no existe
                if weight_key not in st.session_state:
                    st.session_state[weight_key] = default_value
                
                # Input de peso
                st.number_input(
                    f"{symbol}",
                    min_value=0,
                    max_value=100,
                    step=1,
                    key=weight_key,
                    help="%"
                )
        
        submitted = st.form_submit_button(
            "💼 Aplicar pesos",
            width='stretch'
        )
    
    # Leer valores SOLO CUANDO se pulsa el botón (FUERA del form)
    weights_str = ""
    if submitted and symbols_list:
            weights_inputs = []
            for symbol in symbols_list:
                weight_key = f"weight_{symbol}"
                percent_value = st.session_state.get(weight_key, 0)
                weight = percent_value / 100.0
                weights_inputs.append(weight)
            
            total_weight = sum(weights_inputs)
            # Usar rango más amplio para tolerar redondeos (ej: 33%+33%+33%=99%)
            if 0.98 <= total_weight <= 1.02:
                st.success(f"✅ Total: {total_weight:.1%}")
                weights_str = ",".join([str(w) for w in weights_inputs])
            elif total_weight == 0:
                st.info("💡 Suma 0%. Se usarán pesos iguales.")
                equal_weight = 1.0 / len(symbols_list)
                weights_inputs = [equal_weight] * len(symbols_list)
                weights_str = ",".join([str(w) for w in weights_inputs])
            elif total_weight > 1.02:
                st.error(f"❌ Total: {total_weight:.1%} - Los pesos suman más del 100%. Corrígelos antes de continuar.")
                # No calcular weights_str, queda vacío y el botón no funcionará
            else:  # total_weight < 0.98
                st.warning(f"⚠️ Total: {total_weight:.1%} (suma menos de 100%)")
                # Normalizar a 1.0
                weights_inputs = [w / total_weight for w in weights_inputs]
                weights_str = ",".join([str(w) for w in weights_inputs])
    
    # Si no hay símbolos, usar peso por defecto
    weights_str_final = weights_str if weights_str else "1.0"
    
    return submitted, CarteraParams(symbols_input, weights_str_final, float(valor_inicial_input))

