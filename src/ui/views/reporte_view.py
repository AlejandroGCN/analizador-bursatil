from __future__ import annotations
import streamlit as st
from ui.sidebars import ReporteParams


def tab_reporte(submit: bool, params: ReporteParams | None) -> None:
    """Contenido central de la pestaña 📋 Reporte."""
    st.subheader("📋 Reporte de Análisis")
    
    # Verificar si hay cartera configurada
    if "portfolio_symbols" not in st.session_state or "portfolio_weights" not in st.session_state:
        st.info("💡 Primero configura una cartera en la pestaña '💼 Cartera'.")
        return
    
    # Verificar si hay datos disponibles
    if "last_data_map" not in st.session_state:
        st.info("💡 Primero descarga datos en la pestaña '📊 Datos'.")
        return
    
    if submit and params is not None:
        try:
            from simulation import Portfolio
            
            # Obtener datos históricos
            data_map = st.session_state["last_data_map"]
            
            # Extraer símbolos y crear DataFrame de precios
            prices_dict = {}
            for symbol, data_info in data_map.items():
                if isinstance(data_info, dict) and "data" in data_info:
                    df = data_info["data"]
                else:
                    df = getattr(data_info, "data", None)
                
                if df is not None:
                    # Extraer columna de cierre
                    close_col = next((c for c in df.columns if c.lower() == 'close'), None)
                    if close_col:
                        prices_dict[symbol] = df[close_col]
            
            if not prices_dict:
                st.error("No se pudieron extraer precios de los datos.")
                return
            
            # Crear DataFrame de precios
            import pandas as pd
            prices_df = pd.DataFrame(prices_dict)
            
            # Obtener cartera configurada
            portfolio_symbols = st.session_state["portfolio_symbols"]
            portfolio_weights = st.session_state["portfolio_weights"]
            
            # Verificar que todos los símbolos de la cartera estén en los datos
            available_symbols = set(prices_dict.keys())
            portfolio_symbols_set = set(portfolio_symbols)
            
            if portfolio_symbols_set.issubset(available_symbols):
                # Filtrar solo los símbolos disponibles y reajustar pesos
                symbols_in_data = [s for s in portfolio_symbols if s in available_symbols]
                if len(symbols_in_data) == len(portfolio_symbols):
                    symbols = portfolio_symbols
                    weights = portfolio_weights
                else:
                    # Algunos símbolos faltan, reajustar pesos
                    symbol_to_weight = dict(zip(portfolio_symbols, portfolio_weights))
                    symbols = symbols_in_data
                    filtered_weights = [symbol_to_weight[s] for s in symbols]
                    total_weight = sum(filtered_weights)
                    weights = [w / total_weight for w in filtered_weights]
            else:
                st.error("⚠️ La cartera configurada no coincide con los datos descargados.")
                return
            
            # Crear cartera
            portfolio = Portfolio(
                name="Mi Cartera",
                symbols=symbols,
                weights=weights
            )
            portfolio.set_prices(prices_df)
            
            # Guardar cartera en session state
            st.session_state["reporte_portfolio"] = portfolio
            
            st.success("✅ Reporte generado exitosamente!")
        
        except Exception as e:
            st.error(f"❌ Error generando reporte: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # Mostrar reporte si existe
    if "reporte_portfolio" in st.session_state:
        portfolio = st.session_state["reporte_portfolio"]
        _show_portfolio_report(portfolio)
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

