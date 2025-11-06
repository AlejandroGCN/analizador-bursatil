"""
Vista de simulación Monte Carlo.

Permite simular tanto carteras completas como activos individuales usando el modelo
de movimiento browniano geométrico para proyecciones de rendimiento.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from numpy.random import default_rng
import matplotlib.pyplot as plt
from typing import Any, Optional
from ui.sidebars import MonteCarloParams
import sys
import os
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300, max_entries=5)
def _create_distribution_charts(final_values_tuple: tuple) -> bytes:
    """Crea gráficos de distribución (histograma y box plot) cacheados."""
    final_values = pd.Series(final_values_tuple)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histograma
    ax1.hist(final_values, bins=50, edgecolor='black', alpha=0.7)
    ax1.axvline(final_values.mean(), color='red', linestyle='--', label='Media')
    ax1.axvline(final_values.median(), color='green', linestyle='--', label='Mediana')
    ax1.set_xlabel('Valor final ($)')
    ax1.set_ylabel('Frecuencia')
    ax1.set_title('Distribución del valor final')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    ax2.boxplot([final_values], vert=True)
    ax2.set_ylabel('Valor final ($)')
    ax2.set_title('Box Plot del valor final')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Convertir a bytes para cache
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def _render_distribution_charts(final_values: pd.Series) -> None:
    """Renderiza gráficos de distribución usando cache."""
    final_values_tuple = tuple(final_values.values)
    chart_bytes = _create_distribution_charts(final_values_tuple)
    st.image(chart_bytes)


def _get_prices_from_data_map(data_map: dict) -> dict:
    """
    Obtiene precios de cierre desde data_map.
    
    Args:
        data_map: Diccionario con datos de series temporales por símbolo
    
    Returns:
        Diccionario con precios de cierre por símbolo
    """
    prices_dict = {}
    for symbol, data_info in data_map.items():
        if isinstance(data_info, dict) and "data" in data_info:
            df = data_info["data"]
        else:
            df = getattr(data_info, "data", None)
        
        if df is not None:
            # Verificar si es DataFrame o Series
            if isinstance(df, pd.DataFrame):
                close_col = next((c for c in df.columns if c.lower() == 'close'), None)
                if close_col:
                    prices_dict[symbol] = df[close_col]
            elif isinstance(df, pd.Series):
                # Si es Series, usarlo directamente
                prices_dict[symbol] = df
    return prices_dict


# Importar funciones compartidas de utils para evitar duplicación
from ui.utils import (
    normalize_symbol as _normalize_symbol,
    create_normalized_symbol_dicts as _create_normalized_symbol_dicts_wrapper
)

def _create_normalized_symbol_dicts(
    prices_dict: dict, 
    portfolio_symbols: list[str]
) -> tuple[dict, dict]:
    """
    Crea diccionarios de símbolos normalizados para comparación.
    
    Args:
        prices_dict: Diccionario con precios por símbolo original
        portfolio_symbols: Lista de símbolos de la cartera
    
    Returns:
        Tuple con (diccionario símbolos disponibles, diccionario símbolos cartera)
    """
    return _create_normalized_symbol_dicts_wrapper(list(prices_dict.keys()), portfolio_symbols)


def _get_equal_weights_for_available_symbols(
    missing_normalized: set,
    portfolio_symbols_dict: dict,
    portfolio_symbols: list[str],
    prices_dict: dict
) -> tuple[list, list]:
    """
    Obtiene pesos iguales para símbolos disponibles cuando faltan algunos.
    
    Args:
        missing_normalized: Set de símbolos faltantes normalizados
        portfolio_symbols_dict: Mapeo símbolo normalizado -> original
        portfolio_symbols: Lista original de símbolos de cartera
        prices_dict: Diccionario con precios disponibles
    
    Returns:
        Tuple con (lista de símbolos, lista de pesos)
    """
    missing_original = [
        portfolio_symbols_dict[norm] 
        for norm in missing_normalized 
        if norm in portfolio_symbols_dict
    ]
    
    logger.info(f"Símbolos faltantes en datos: {missing_original} (mostrado en UI)")
    
    st.warning(
        f"⚠️ La cartera configurada no coincide con los datos descargados.\n\n"
        f"**Símbolos faltantes en los datos:** {', '.join(missing_original)}\n\n"
        f"**Símbolos en cartera:** {', '.join(portfolio_symbols)}\n"
        f"**Símbolos disponibles en datos:** {', '.join(prices_dict.keys())}\n\n"
        f"Usando pesos iguales para los símbolos disponibles."
    )
    
    symbols = list(prices_dict.keys())
    n_assets = len(symbols)
    weights = [1.0 / n_assets] * n_assets
    st.info(f"📊 Usando pesos iguales (1/{n_assets} = {1.0/n_assets:.2%} cada uno)")
    return symbols, weights


# Importar función compartida de utils
from ui.utils import get_symbols_mapped_to_data_format as _get_symbols_mapped_to_data_format


def _calculate_adjusted_weights_for_partial_match(
    symbols_in_data: list[str],
    portfolio_symbols: list[str],
    portfolio_weights: list[float],
    portfolio_symbols_dict: dict,
    available_symbols_normalized: set,
    portfolio_symbols_set_normalized: set
) -> tuple[list, list]:
    """
    Calcula pesos ajustados cuando algunos símbolos no están disponibles.
    
    Args:
        symbols_in_data: Símbolos disponibles en formato de datos
        portfolio_symbols: Lista original de símbolos de cartera
        portfolio_weights: Pesos originales de la cartera
        portfolio_symbols_dict: Mapeo símbolo normalizado -> original
        available_symbols_normalized: Set de símbolos disponibles normalizados
        portfolio_symbols_set_normalized: Set de símbolos de cartera normalizados
    
    Returns:
        Tuple con (lista de símbolos, lista de pesos ajustados)
    """
    missing = portfolio_symbols_set_normalized - available_symbols_normalized
    missing_original = [
        portfolio_symbols_dict[norm] 
        for norm in missing 
        if norm in portfolio_symbols_dict
    ]
    
    st.warning(
        f"⚠️ Algunos activos configurados no están en los datos: {', '.join(missing_original)}. "
        f"Ajustando pesos..."
    )
    
    symbol_to_weight = dict(zip(portfolio_symbols, portfolio_weights))
    symbols = symbols_in_data
    filtered_weights = [symbol_to_weight[s] for s in symbols if s in symbol_to_weight]
    total_weight = sum(filtered_weights)
    
    logger.debug(f"  Pesos filtrados: {filtered_weights}, total: {total_weight}")
    
    if total_weight > 0:
        weights = [w / total_weight for w in filtered_weights]
        logger.debug(f"  Pesos normalizados: {weights}")
    else:
        n_assets = len(symbols)
        weights = [1.0 / n_assets] * n_assets
        logger.debug(f"  Total peso es 0, usando pesos iguales: {weights}")
    
    st.info(f"📊 Usando {len(symbols)} activos disponibles con pesos ajustados")
    return symbols, weights


def _get_portfolio_weights(prices_dict: dict) -> tuple[list, list]:
    """
    Obtiene símbolos y pesos de la cartera para simulación.
    
    Maneja la lógica de mapeo entre símbolos de cartera configurada y símbolos
    disponibles en los datos descargados, normalizando símbolos para comparación.
    
    Args:
        prices_dict: Diccionario con precios de cierre por símbolo
    
    Returns:
        Tuple con (lista de símbolos, lista de pesos normalizados)
    """
    if not prices_dict:
        return [], []
    
    # Caso 1: No hay cartera configurada - usar pesos iguales
    if "portfolio_symbols" not in st.session_state or "portfolio_weights" not in st.session_state:
        symbols = list(prices_dict.keys())
        n_assets = len(symbols)
        weights = [1.0 / n_assets] * n_assets
        logger.debug(f"No hay cartera configurada, usando pesos iguales: {symbols} -> {weights}")
        st.info(f"📊 Usando pesos iguales (1/{n_assets} = {1.0/n_assets:.2%} cada uno)")
        return symbols, weights
    
    portfolio_symbols = st.session_state["portfolio_symbols"]
    portfolio_weights = st.session_state["portfolio_weights"]
    
    logger.info("🔍 Comparando cartera vs datos:")
    logger.info(f"  Cartera símbolos: {portfolio_symbols}")
    logger.info(f"  Datos disponibles: {list(prices_dict.keys())}")
    logger.debug(f"  Pesos de cartera: {portfolio_weights}")
    
    # Crear diccionarios normalizados
    available_symbols_dict, portfolio_symbols_dict = _create_normalized_symbol_dicts(
        prices_dict, portfolio_symbols
    )
    
    available_symbols_normalized = set(available_symbols_dict.keys())
    portfolio_symbols_set_normalized = set(portfolio_symbols_dict.keys())
    
    logger.info(f"  Símbolos normalizados cartera: {portfolio_symbols_set_normalized}")
    logger.info(f"  Símbolos normalizados rin: {available_symbols_normalized}")
    
    # Caso 2: Hay símbolos faltantes
    missing_normalized = portfolio_symbols_set_normalized - available_symbols_normalized
    if missing_normalized:
        return _get_equal_weights_for_available_symbols(
            missing_normalized, portfolio_symbols_dict, portfolio_symbols, prices_dict
        )
    
    # Caso 3: Mapear símbolos a formato de datos
    symbols_in_data = _get_symbols_mapped_to_data_format(portfolio_symbols, available_symbols_dict)
    
    # Caso 4: Todos los símbolos están disponibles
    if len(symbols_in_data) == len(portfolio_symbols):
        logger.info(f"✅ Todos los símbolos coinciden. Usando: {symbols_in_data}")
        logger.debug(f"  Pesos asignados: {portfolio_weights}")
        logger.debug(f"  Mapeo: {dict(zip(portfolio_symbols, symbols_in_data))}")
        st.info(f"💼 Usando cartera configurada con {len(portfolio_symbols)} activos")
        return symbols_in_data, portfolio_weights
    
    # Caso 5: Algunos símbolos no coinciden (caso edge)
    return _calculate_adjusted_weights_for_partial_match(
        symbols_in_data, portfolio_symbols, portfolio_weights,
        portfolio_symbols_dict, available_symbols_normalized, portfolio_symbols_set_normalized
    )


def _display_individual_stats(portfolio: Any, symbol: str, results: pd.DataFrame) -> None:
    """
    Muestra estadísticas para simulación individual de un activo.
    
    Args:
        portfolio: Objeto Portfolio con datos del activo
        symbol: Símbolo del activo simulado
        results: DataFrame con resultados de simulación
    """
    st.info(f"📊 Simulación individual para: **{symbol}**")
    
    if portfolio.returns is None:
        return
    
    asset_return = portfolio.returns[symbol].mean()
    asset_vol = portfolio.returns[symbol].std() * (252 ** 0.5)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Retorno esperado (anual)", f"{asset_return * 252:.2%}")
    with col2:
        st.metric("Volatilidad (anual)", f"{asset_vol:.2%}")
    with col3:
        initial_value = results.iloc[0, 0]
        final_mean = results.iloc[:, -1].mean()
        retorno_simulado = ((final_mean / initial_value) - 1) * 100
        st.metric("Retorno simulado", f"{retorno_simulado:.2f}%")


def _display_portfolio_stats(portfolio: Any) -> None:
    """
    Muestra estadísticas para simulación de cartera completa.
    
    Args:
        portfolio: Objeto Portfolio con datos de la cartera
    """
    stats = portfolio.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Retorno esperado (anual)", f"{stats['return'] * 252:.2%}")
    with col2:
        st.metric("Volatilidad (anual)", f"{stats['volatility']:.2%}")
    with col3:
        st.metric("Sharpe Ratio", f"{stats['sharpe_ratio']:.3f}")
    with col4:
        st.metric("Nº de Activos", len(portfolio.symbols))


def _run_individual_simulation(
    params: MonteCarloParams,
    prices_dict: dict,
    prices_df: pd.DataFrame
) -> tuple[pd.DataFrame, Any]:
    """
    Ejecuta simulación Monte Carlo para un activo individual.
    
    Args:
        params: Parámetros de simulación
        prices_dict: Diccionario con precios por símbolo
        prices_df: DataFrame con precios
    
    Returns:
        Tuple con (resultados de simulación, objeto Portfolio)
    
    Raises:
        ValueError: Si el símbolo no está disponible
    """
    from simulation import Portfolio
    
    if not params.symbol_individual or params.symbol_individual not in prices_dict:
        raise ValueError(f"Símbolo '{params.symbol_individual}' no disponible en los datos.")
    
    portfolio = Portfolio(
        name=f"Portfolio Individual - {params.symbol_individual}",
        symbols=[params.symbol_individual],
        weights=[1.0]
    )
    portfolio.set_prices(prices_df[[params.symbol_individual]])
    
    results = portfolio.monte_carlo_simulation_individual(
        symbol=params.symbol_individual,
        n_simulations=params.nsims,
        time_horizon=params.horizonte,
        initial_value=None,
        dynamic_volatility=params.vol_dinamica,
        random_seed=42
    )
    
    return results, portfolio


def _run_portfolio_simulation(
    params: MonteCarloParams,
    prices_dict: dict,
    prices_df: pd.DataFrame
) -> tuple[pd.DataFrame, Any]:
    """
    Ejecuta simulación Monte Carlo para cartera completa.
    
    Args:
        params: Parámetros de simulación
        prices_dict: Diccionario con precios por símbolo
        prices_df: DataFrame con precios
    
    Returns:
        Tuple con (resultados de simulación, objeto Portfolio)
    """
    from simulation import Portfolio
    
    symbols, weights = _get_portfolio_weights(prices_dict)
    
    portfolio = Portfolio(
        name="Portfolio",
        symbols=symbols,
        weights=weights
    )
    portfolio.set_prices(prices_df)
    
    results = portfolio.monte_carlo_simulation(
        n_simulations=params.nsims,
        time_horizon=params.horizonte,
        initial_value=params.valor_inicial,
        dynamic_volatility=params.vol_dinamica,
        random_seed=42
    )
    
    return results, portfolio


def tab_montecarlo(submit: bool, params: MonteCarloParams | None) -> None:
    """
    Contenido central de la pestaña 🎲 Monte Carlo.
    
    Permite ejecutar simulaciones Monte Carlo tanto para cartera completa
    como para activos individuales.
    
    Args:
        submit: Indica si se envió el formulario
        params: Parámetros de simulación (puede ser None)
    """
    st.subheader("🎲 Simulación Monte Carlo")
    
    # Verificar si hay datos disponibles
    if "last_data_map" not in st.session_state:
        st.info("💡 Primero descarga datos en la pestaña '📊 Datos' para poder simular.")
        return
    
    if submit and params is not None:
        try:
            tipo_sim = "cartera completa" if params.tipo_simulacion == "cartera" else f"activo {params.symbol_individual}"
            with st.spinner(f"🎲 Ejecutando {params.nsims:,} simulaciones Monte Carlo para {tipo_sim}... Esto puede tomar unos segundos."):
                data_map = st.session_state["last_data_map"]
                
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
                
                prices_dict = _get_prices_from_data_map(data_map)
                if not prices_dict:
                    st.error("No se pudieron extraer precios de los datos.")
                    return
                
                prices_df = pd.DataFrame(prices_dict)
                
                # Ejecutar simulación según tipo
                if params.tipo_simulacion == "individual":
                    results, portfolio = _run_individual_simulation(params, prices_dict, prices_df)
                    st.session_state["montecarlo_sim_type"] = "individual"
                    st.session_state["montecarlo_symbol"] = params.symbol_individual
                else:
                    results, portfolio = _run_portfolio_simulation(params, prices_dict, prices_df)
                    st.session_state["montecarlo_sim_type"] = "cartera"
                
                st.session_state["montecarlo_results"] = results
                st.session_state["montecarlo_portfolio"] = portfolio
                
                sim_type_text = "individual" if params.tipo_simulacion == "individual" else "de cartera"
                st.success(f"✅ Simulación {sim_type_text} completada exitosamente!")
            
            _show_montecarlo_results(results, portfolio)
            
        except Exception as e:
            logger.error(f"Error en simulación: {e}", exc_info=True)
            st.error(f"❌ Error en simulación: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    elif "montecarlo_results" in st.session_state:
        st.info("Mostrando último resultado de simulación.")
        _show_montecarlo_results(
            st.session_state["montecarlo_results"],
            st.session_state.get("montecarlo_portfolio")
        )
    else:
        st.info("💡 Configura los parámetros de simulación en el panel lateral y ejecuta la simulación.")


def _show_montecarlo_results(results: pd.DataFrame, portfolio: Any) -> None:
    """
    Muestra los resultados de la simulación Monte Carlo.
    
    Args:
        results: DataFrame con resultados de simulación
        portfolio: Objeto Portfolio con datos de la cartera o activo
    """
    sim_type = st.session_state.get("montecarlo_sim_type", "cartera")
    symbol_individual = st.session_state.get("montecarlo_symbol", "")
    
    # Estadísticas de la cartera o activo
    if portfolio is not None:
        if sim_type == "individual" and symbol_individual:
            _display_individual_stats(portfolio, symbol_individual, results)
        else:
            _display_portfolio_stats(portfolio)
        
        st.divider()
    
    # Estadísticas del valor final
    final_values = results.iloc[:, -1]
    
    st.subheader("📊 Estadísticas del valor final")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Distribución del valor final:**")
        stats_dict = {
            "Media": f"${final_values.mean():,.2f}",
            "Mediana": f"${final_values.median():,.2f}",
            "Std Dev": f"${final_values.std():,.2f}",
            "Mínimo": f"${final_values.min():,.2f}",
            "Máximo": f"${final_values.max():,.2f}"
        }
        for key, value in stats_dict.items():
            st.write(f"- **{key}**: {value}")
    
    with col2:
        st.write("**Percentiles:**")
        percentiles_dict = {
            "5%": final_values.quantile(0.05),
            "25%": final_values.quantile(0.25),
            "50%": final_values.quantile(0.50),
            "75%": final_values.quantile(0.75),
            "95%": final_values.quantile(0.95)
        }
        for key, value in percentiles_dict.items():
            st.write(f"- **{key}**: ${value:,.2f}")
    
    st.divider()
    
    # Histograma del valor final (ya cacheado) - PRIMERO porque es más rápido
    st.subheader("📊 Distribución del valor final")
    with st.spinner("Generando gráficos de distribución..."):
        _render_distribution_charts(final_values)
    
    st.divider()
    
    # Gráfico de trayectorias (con expander para lazy loading - mantiene interactividad)
    with st.expander("📈 Ver trayectorias de simulación", expanded=False):
        sample_size = min(50, len(results))
        rng = default_rng(seed=42)
        sample_indices = rng.choice(len(results), sample_size, replace=False)
        sample_results = results.iloc[sample_indices]
        
        # Usar st.line_chart nativo de Streamlit (más bonito e interactivo)
        st.line_chart(sample_results.T, height=400)
        st.caption(f"ℹ️ Se ejecutaron **{len(results):,} simulaciones**. El gráfico muestra **{sample_size} muestras representativas** para claridad visual.")
    
    # Tabla de resumen en expander (solo columnas clave para reducir carga)
    with st.expander("📋 Ver tabla de resumen estadístico", expanded=False):
        num_cols = results.shape[1]
        if num_cols > 30:
            # Para horizonte largo, mostrar subconjunto
            key_cols = [0, num_cols//4, num_cols//2, 3*num_cols//4, num_cols-1]
            st.dataframe(results.iloc[:, key_cols].describe(), width='stretch')
            st.caption(f"ℹ️ Mostrando 5 días clave de {num_cols} días simulados (día 0, {num_cols//4}, {num_cols//2}, {3*num_cols//4}, {num_cols-1})")
        else:
            st.dataframe(results.describe(), width='stretch')
