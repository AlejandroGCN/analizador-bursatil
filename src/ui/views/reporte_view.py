from __future__ import annotations
from typing import Any
import streamlit as st
import pandas as pd
import logging
from ui.sidebars import ReporteParams
from ui.views.montecarlo_view import _get_prices_from_data_map

logger = logging.getLogger(__name__)


def _check_prerequisites() -> bool:
    """Verifica que existan los prerrequisitos para generar el reporte."""
    missing_steps = []
    
    if "portfolio_symbols" not in st.session_state or "portfolio_weights" not in st.session_state:
        missing_steps.append("💼 Configura una cartera en la pestaña 'Cartera'")
    
    if "last_data_map" not in st.session_state:
        missing_steps.append("📊 Descarga datos en la pestaña 'Datos'")
    
    # Validar que los datos sean precios históricos (no retornos)
    last_kind = st.session_state.get("last_kind", "ohlcv")
    if last_kind != "ohlcv":
        missing_steps.append(f"📊 Cambia el tipo de datos a 'Precios Históricos' (actualmente: '{last_kind}')")
    
    if missing_steps:
        st.warning("⚠️ **Faltan pasos previos para generar el reporte:**")
        for step in missing_steps:
            st.markdown(f"- {step}")
        st.info("💡 Completa los pasos anteriores y regresa aquí para ver el reporte completo.")
        return False
    
    return True


def _adjust_weights_for_available_symbols(
    portfolio_symbols: list[str], 
    portfolio_weights: list[float], 
    available_symbols: list[str]
) -> Optional[tuple[list[str], list[float]]]:
    """
    Ajusta los pesos si faltan algunos símbolos en los datos.
    
    Utiliza funciones compartidas de ui.utils para evitar duplicación de código.
    
    Args:
        portfolio_symbols: Lista de símbolos de la cartera
        portfolio_weights: Lista de pesos de la cartera
        available_symbols: Lista de símbolos disponibles en los datos
    
    Returns:
        Tuple con (símbolos ajustados, pesos ajustados) o None si faltan símbolos críticos
    """
    from ui.utils import (
        normalize_symbol,
        create_normalized_symbol_dicts,
        get_symbols_mapped_to_data_format
    )
    
    # Crear diccionarios normalizados
    available_symbols_dict, portfolio_symbols_dict = create_normalized_symbol_dicts(
        available_symbols, portfolio_symbols
    )
    
    available_symbols_normalized = set(available_symbols_dict.keys())
    portfolio_symbols_set_normalized = set(portfolio_symbols_dict.keys())
    
    # Verificar si faltan símbolos
    if not portfolio_symbols_set_normalized.issubset(available_symbols_normalized):
        missing = portfolio_symbols_set_normalized - available_symbols_normalized
        missing_original = [
            portfolio_symbols_dict[norm] 
            for norm in missing 
            if norm in portfolio_symbols_dict
        ]
        st.error(
            f"⚠️ La cartera configurada no coincide con los datos descargados. "
            f"Símbolos faltantes: {', '.join(missing_original)}"
        )
        return None
    
    # Mapear símbolos al formato de datos
    symbols_in_data = get_symbols_mapped_to_data_format(
        portfolio_symbols, available_symbols_dict
    )
    
    # Si todos los símbolos están disponibles y coinciden, retornar directamente
    if len(symbols_in_data) == len(portfolio_symbols):
        return symbols_in_data, portfolio_weights
    
    # Ajustar pesos si faltan algunos símbolos
    symbol_to_weight = dict(zip(portfolio_symbols, portfolio_weights))
    filtered_weights = [symbol_to_weight[s] for s in symbols_in_data if s in symbol_to_weight]
    total_weight = sum(filtered_weights)
    
    if total_weight > 0:
        weights = [w / total_weight for w in filtered_weights]
    else:
        # Si no hay peso, usar pesos iguales
        n_assets = len(symbols_in_data)
        weights = [1.0 / n_assets] * n_assets
    
    return symbols_in_data, weights


@st.cache_data(ttl=300, show_spinner=False)
def _create_portfolio_from_data_cached(
    portfolio_symbols_tuple: tuple,
    portfolio_weights_tuple: tuple,
    data_map_hash: str
) -> tuple:
    """
    Crea un objeto Portfolio a partir de los datos disponibles (cacheado).
    
    Retorna tupla serializable para el cache.
    """
    from simulation import Portfolio
    
    logger.info("📋 Creando portfolio para reporte")
    
    data_map = st.session_state["last_data_map"]
    prices_dict = _get_prices_from_data_map(data_map)
    
    logger.debug(f"  Precios extraídos: {len(prices_dict)} símbolos")
    logger.debug(f"  Símbolos en precios: {list(prices_dict.keys())}")
    
    if not prices_dict:
        logger.error("No se pudieron extraer precios de los datos")
        return None, None, None
    
    prices_df = pd.DataFrame(prices_dict)
    portfolio_symbols = list(portfolio_symbols_tuple)
    portfolio_weights = list(portfolio_weights_tuple)
    available_symbols = list(prices_dict.keys())
    
    logger.debug(f"  Símbolos de cartera: {portfolio_symbols}")
    logger.debug(f"  Pesos de cartera: {portfolio_weights}")
    logger.debug(f"  Símbolos disponibles en datos: {available_symbols}")
    
    symbols, weights = _adjust_weights_for_available_symbols(
        portfolio_symbols, portfolio_weights, available_symbols
    )
    
    if symbols is None or weights is None:
        logger.info("No se pudo ajustar cartera - símbolos no coinciden (mostrado en UI)")
        return None, None, None
    
    logger.debug(f"  Símbolos ajustados: {symbols}")
    logger.debug(f"  Pesos ajustados: {weights}")
    logger.debug(f"  Suma de pesos: {sum(weights):.6f}")
    
    portfolio = Portfolio(name="Mi Cartera", symbols=symbols, weights=weights)
    portfolio.set_prices(prices_df)
    
    logger.info(f"✅ Portfolio creado exitosamente con {len(symbols)} activos")
    
    # Retornar datos serializables para recrear el portfolio
    return tuple(symbols), tuple(weights), prices_df.to_dict()


def _create_portfolio_from_data():
    """Wrapper para crear portfolio usando cache."""
    portfolio_symbols = st.session_state.get("portfolio_symbols", [])
    portfolio_weights = st.session_state.get("portfolio_weights", [])
    data_map = st.session_state.get("last_data_map", {})
    
    # Crear hash simple para invalidar cache cuando cambian los datos
    data_map_hash = str(hash(str(sorted(data_map.keys()))))
    
    symbols_tuple, weights_tuple, prices_dict = _create_portfolio_from_data_cached(
        tuple(portfolio_symbols),
        tuple(portfolio_weights),
        data_map_hash
    )
    
    if symbols_tuple is None:
        st.error("No se pudieron extraer precios de los datos.")
        return None
    
    # Recrear portfolio desde datos cacheados
    from simulation import Portfolio
    portfolio = Portfolio(name="Mi Cartera", symbols=list(symbols_tuple), weights=list(weights_tuple))
    portfolio.set_prices(pd.DataFrame(prices_dict))
    
    return portfolio


def tab_reporte(submit: bool, params: ReporteParams | None) -> None:
    """Contenido central de la pestaña 📋 Reporte."""
    st.subheader("📋 Reporte de Análisis")
    
    if not _check_prerequisites():
        return
    
    if submit and params is not None:
        try:
            with st.spinner("📊 Generando reporte completo de la cartera..."):
                portfolio = _create_portfolio_from_data()
                if portfolio:
                    st.session_state["reporte_portfolio"] = portfolio
                    num_symbols = len(portfolio.symbols)
                    st.success(f"✅ **Reporte generado exitosamente** para cartera con {num_symbols} activo(s)")
        except Exception as e:
            st.error(f"❌ Error generando reporte: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    if "reporte_portfolio" in st.session_state:
        _show_portfolio_report(st.session_state["reporte_portfolio"])
    else:
        st.info("💡 Configura los parámetros del reporte en el panel lateral y genera el reporte.")


def _show_portfolio_report(portfolio: Any) -> None:
    """
    Muestra el reporte completo de la cartera.
    
    Args:
        portfolio: Objeto Portfolio con los datos de la cartera
    """
    logger.info("📊 Generando reporte de cartera")
    
    # Log de estadísticas antes de generar reporte
    try:
        stats = portfolio.get_statistics()
        logger.debug("  Estadísticas de cartera:")
        logger.debug(f"    Retorno: {stats['return']:.6f} (diario), {stats['return']*252:.4%} (anualizado)")
        logger.debug(f"    Volatilidad: {stats['volatility']:.4%}")
        logger.debug(f"    Sharpe Ratio: {stats['sharpe_ratio']:.4f}")
        logger.debug(f"    Número de activos: {stats['num_assets']}")
    except Exception as e:
        logger.warning(f"Error obteniendo estadísticas: {e}")
    
    from reporting import MonteCarloReporter
    
    # Usar el generador de reportes del módulo reporting
    MonteCarloReporter.show_portfolio_report(portfolio)
    
    logger.info("✅ Reporte generado y mostrado")

