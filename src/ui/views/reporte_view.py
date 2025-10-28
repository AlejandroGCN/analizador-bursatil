from __future__ import annotations
from typing import Any
import streamlit as st
import pandas as pd
from ui.sidebars import ReporteParams
from ui.views.montecarlo_view import _extract_prices_from_data_map


def _check_prerequisites() -> bool:
    """Verifica que existan los prerrequisitos para generar el reporte."""
    if "portfolio_symbols" not in st.session_state or "portfolio_weights" not in st.session_state:
        st.info("💡 Primero configura una cartera en la pestaña '💼 Cartera'.")
        return False
    if "last_data_map" not in st.session_state:
        st.info("💡 Primero descarga datos en la pestaña '📊 Datos'.")
        return False
    return True


def _adjust_weights_for_available_symbols(portfolio_symbols, portfolio_weights, available_symbols):
    """Ajusta los pesos si faltan algunos símbolos en los datos."""
    symbols_in_data = [s for s in portfolio_symbols if s in available_symbols]
    if len(symbols_in_data) == len(portfolio_symbols):
        return portfolio_symbols, portfolio_weights
    
    symbol_to_weight = dict(zip(portfolio_symbols, portfolio_weights))
    filtered_weights = [symbol_to_weight[s] for s in symbols_in_data]
    total_weight = sum(filtered_weights)
    weights = [w / total_weight for w in filtered_weights]
    return symbols_in_data, weights


def _create_portfolio_from_data():
    """Crea un objeto Portfolio a partir de los datos disponibles."""
    from simulation import Portfolio
    
    data_map = st.session_state["last_data_map"]
    prices_dict = _extract_prices_from_data_map(data_map)
    
    if not prices_dict:
        st.error("No se pudieron extraer precios de los datos.")
        return None
    
    prices_df = pd.DataFrame(prices_dict)
    portfolio_symbols = st.session_state["portfolio_symbols"]
    portfolio_weights = st.session_state["portfolio_weights"]
    available_symbols = set(prices_dict.keys())
    portfolio_symbols_set = set(portfolio_symbols)
    
    if not portfolio_symbols_set.issubset(available_symbols):
        st.error("⚠️ La cartera configurada no coincide con los datos descargados.")
        return None
    
    symbols, weights = _adjust_weights_for_available_symbols(
        portfolio_symbols, portfolio_weights, available_symbols
    )
    
    portfolio = Portfolio(name="Mi Cartera", symbols=symbols, weights=weights)
    portfolio.set_prices(prices_df)
    return portfolio


def tab_reporte(submit: bool, params: ReporteParams | None) -> None:
    """Contenido central de la pestaña 📋 Reporte."""
    st.subheader("📋 Reporte de Análisis")
    
    if not _check_prerequisites():
        return
    
    if submit and params is not None:
        try:
            portfolio = _create_portfolio_from_data()
            if portfolio:
                st.session_state["reporte_portfolio"] = portfolio
                st.success("✅ Reporte generado exitosamente!")
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
    from reporting import MonteCarloReporter
    
    # Usar el generador de reportes del módulo reporting
    MonteCarloReporter.show_portfolio_report(portfolio)

