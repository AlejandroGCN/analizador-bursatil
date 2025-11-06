from __future__ import annotations
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import logging
from io import BytesIO
from ui.sidebars import CarteraParams
from ui.utils import display_symbol_info, render_symbol_input

logger = logging.getLogger(__name__)

# Constantes
DEFAULT_INITIAL_VALUE = 10000.0
WEIGHT_TOLERANCE = 0.01


def _parse_symbols_and_weights(symbols_str: str, weights_str: str) -> tuple[list[str], list[float]]:
    """Parsea y convierte símbolos y pesos desde strings."""
    logger.debug(f"Parsing symbols: '{symbols_str}' | weights: '{weights_str}'")
    symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
    weights_str_list = [w.strip() for w in weights_str.split(",") if w.strip()]
    weights = [float(w) for w in weights_str_list]
    logger.debug(f"Parsed -> symbols: {symbols}, weights: {weights}")
    return symbols, weights


def _validate_portfolio_inputs(symbols: list[str], weights: list[float]) -> bool:
    """Valida que los inputs de cartera sean correctos."""
    if not symbols:
        st.error("❌ Debes especificar al menos un activo.")
        return False
    
    if len(weights) != len(symbols):
        st.error(
            f"❌ Número de pesos ({len(weights)}) debe coincidir con número de símbolos ({len(symbols)})."
        )
        return False
    
    return True


def _normalize_weights_if_needed(weights: list[float]) -> tuple[list[float], list[float]]:
    """
    Normaliza los pesos si no suman aproximadamente 1.0.
    Retorna (pesos_normalizados, pesos_originales).
    """
    total_weight = sum(weights)
    original_weights = weights.copy()
    logger.debug(f"Normalizando pesos: {weights}, suma: {total_weight}")
    
    if not (1.0 - WEIGHT_TOLERANCE <= total_weight <= 1.0 + WEIGHT_TOLERANCE):
        logger.info(f"Pesos no suman 1.0 (suman {total_weight}), normalizando automáticamente")
        st.warning(f"⚠️ Los pesos suman {total_weight:.1%}. Normalizando para cálculos internos.")
        weights = [w / total_weight for w in weights]
        logger.debug(f"Pesos normalizados: {weights}, nueva suma: {sum(weights)}")
    
    return weights, original_weights


def _save_portfolio_to_session(
    symbols: list[str],
    weights: list[float],
    original_weights: list[float],
    initial_value: float
) -> None:
    """Guarda la configuración de cartera en session_state."""
    st.session_state["portfolio_symbols"] = symbols
    st.session_state["portfolio_weights"] = weights
    st.session_state["portfolio_original_weights"] = original_weights
    st.session_state["portfolio_valor_inicial"] = initial_value
    logger.info(f"✅ Cartera guardada: {symbols} con pesos {weights}")


@st.cache_data(ttl=60, max_entries=10)
def _calculate_dollar_values_cached(weights_tuple: tuple, initial_value: float) -> tuple:
    """Calcula los valores en dólares para cada activo (cacheado)."""
    weights = list(weights_tuple)
    total_weight = sum(weights)
    
    if abs(total_weight - 1.0) > WEIGHT_TOLERANCE:
        normalized_weights = (w / total_weight for w in weights)
        return tuple(w * initial_value for w in normalized_weights)
    
    return tuple(w * initial_value for w in weights)


def _calculate_dollar_values(weights: list[float], initial_value: float) -> list[float]:
    """Calcula los valores en dólares para cada activo."""
    weights_tuple = tuple(weights)
    cached_result = _calculate_dollar_values_cached(weights_tuple, initial_value)
    return list(cached_result)


def _create_portfolio_dataframe(symbols: list[str], weights: list[float], dollar_values: list[float]) -> pd.DataFrame:
    """Crea un DataFrame con la composición de la cartera."""
    return pd.DataFrame({
        "Activo": symbols,
        "Peso (%)": [f"{w*100:.2f}%" for w in weights],
        "Valor ($)": [f"${v:,.2f}" for v in dollar_values]
    })


@st.cache_data(ttl=60, max_entries=5)
def _create_portfolio_chart_figure(symbols: tuple, dollar_values: tuple) -> bytes:
    """Crea y serializa el gráfico de barras de la cartera (cacheado)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.tab10(range(len(symbols)))
    bars = ax.bar(symbols, dollar_values, color=colors)
    
    # Añadir etiquetas en las barras
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f'${height:,.0f}',
            ha='center',
            va='bottom',
            fontsize=11,
            fontweight='bold'
        )
    
    ax.set_xlabel('Activo', fontsize=12, fontweight='bold')
    ax.set_ylabel('Valor ($)', fontsize=12, fontweight='bold')
    ax.set_title('Distribución de valores en la cartera', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    
    # Convertir a bytes para cache
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def _render_portfolio_bar_chart(symbols: list[str], dollar_values: list[float]) -> None:
    """Renderiza un gráfico de barras con la distribución de la cartera (optimizado con cache)."""
    symbols_tuple = tuple(symbols)
    dollar_values_tuple = tuple(dollar_values)
    
    chart_bytes = _create_portfolio_chart_figure(symbols_tuple, dollar_values_tuple)
    st.image(chart_bytes)


def _display_portfolio_info(symbols: list[str], weights: list[float]) -> None:
    """Muestra información detallada de la cartera configurada."""
    initial_value = st.session_state.get("portfolio_valor_inicial", DEFAULT_INITIAL_VALUE)
    
    st.subheader("📋 Composición de la cartera")
    
    dollar_values = _calculate_dollar_values(weights, initial_value)
    portfolio_df = _create_portfolio_dataframe(symbols, weights, dollar_values)
    
    st.dataframe(portfolio_df, width='stretch', hide_index=True)
    
    st.subheader("📊 Distribución visual")
    _render_portfolio_bar_chart(symbols, dollar_values)


def _process_portfolio_submission(params: CarteraParams) -> None:
    """Procesa el envío del formulario de cartera."""
    try:
        logger.info("===== PROCESANDO CARTERA =====")
        logger.info(f"Params: symbols={params.symbols}, weights={params.weights}, valor={params.valor_inicial}")
        
        symbols, weights = _parse_symbols_and_weights(params.symbols, params.weights)
        
        if not _validate_portfolio_inputs(symbols, weights):
            return
        
        normalized_weights, original_weights = _normalize_weights_if_needed(weights)
        
        _save_portfolio_to_session(
            symbols,
            normalized_weights,
            original_weights,
            params.valor_inicial
        )
        
        st.success(f"✅ Cartera configurada con {len(symbols)} activos")
        st.rerun()
        
    except Exception as e:
        logger.error(f"Error configurando cartera: {e}", exc_info=True)
        st.error(f"❌ Error configurando cartera: {e}")
        import traceback
        st.code(traceback.format_exc())


def tab_cartera(submit: bool, params: CarteraParams | None) -> None:
    """Contenido central de la pestaña 💼 Cartera."""
    st.subheader("💼 Construcción de cartera")
    
    logger.info(f"View recibió: submit={submit}, params={params}")
    
    # CSS para ocultar elementos del formulario
    st.markdown("""
        <style>
        div[data-testid="stFormSubmitButton"] {
            display: none !important;
        }
        div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Formulario para capturar Enter en el input de símbolos
    with st.form("form_simbolos_cartera", clear_on_submit=False):
        st.text_input(
            "Símbolos (separados por comas)",
            key="cartera_symbols",
            help="Introduce los símbolos separados por comas (ej: AAPL, MSFT, GOOGL). Tras escribir, pulsa **Enter** para aplicar pesos iguales automáticamente.",
            placeholder="AAPL, MSFT, GOOGL"
        )
        # Botón oculto (necesario para que Enter funcione)
        form_submitted = st.form_submit_button("Submit")
    
    # Si se pulsa Enter, aplicar pesos iguales automáticamente
    if form_submitted:
        symbols_text = st.session_state.get("cartera_symbols", "")
        if symbols_text and symbols_text.strip():
            logger.info("Enter presionado en cartera, aplicando pesos iguales automáticamente")
            symbols = [s.strip() for s in symbols_text.split(",") if s.strip()]
            if symbols:
                # Crear pesos iguales
                equal_weight = 1.0 / len(symbols)
                weights = [equal_weight] * len(symbols)
                weights_str = ", ".join(f"{w:.4f}" for w in weights)
                
                # Actualizar el campo de pesos en session_state
                st.session_state["cartera_weights"] = weights_str
                
                # Crear params y procesar
                from ui.sidebars import CarteraParams
                initial_value = st.session_state.get("portfolio_valor_inicial", DEFAULT_INITIAL_VALUE)
                params_auto = CarteraParams(
                    symbols=symbols_text,
                    weights=weights_str,
                    valor_inicial=initial_value
                )
                _process_portfolio_submission(params_auto)
    
    has_portfolio = (
        "portfolio_symbols" in st.session_state 
        and "portfolio_weights" in st.session_state
    )
    symbols_text = st.session_state.get("cartera_symbols", "")
    
    if not has_portfolio and (not symbols_text or not symbols_text.strip()):
        display_symbol_info(contexto="cartera")
    
    st.divider()

    if submit and params is not None:
        _process_portfolio_submission(params)
    
    if has_portfolio:
        logger.info(f"Mostrando cartera guardada: {st.session_state['portfolio_symbols']}")
        
        display_weights = st.session_state.get(
            "portfolio_original_weights",
            st.session_state["portfolio_weights"]
        )
        
        st.info("Mostrando cartera configurada actual.")
        _display_portfolio_info(st.session_state["portfolio_symbols"], display_weights)
