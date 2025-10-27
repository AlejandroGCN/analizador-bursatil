from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ui.sidebars import MonteCarloParams
import sys
import os


def tab_montecarlo(submit: bool, params: MonteCarloParams | None) -> None:
    """Contenido central de la pestaña 🎲 Monte Carlo."""
    st.subheader("🎲 Simulación Monte Carlo")
    
    # Verificar si hay datos disponibles
    if "last_data_map" not in st.session_state:
        st.info("💡 Primero descarga datos en la pestaña '📊 Datos' para poder simular.")
        return
    
    if submit and params is not None:
        try:
            with st.spinner(f"Ejecutando {params.nsims} simulaciones..."):
                # Obtener datos históricos
                data_map = st.session_state["last_data_map"]
                
                # Crear cartera desde los datos
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
                from simulation import Portfolio
                
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
                prices_df = pd.DataFrame(prices_dict)
                
                # Usar cartera configurada si existe y coincide con los datos descargados
                if "portfolio_symbols" in st.session_state and "portfolio_weights" in st.session_state:
                    portfolio_symbols = st.session_state["portfolio_symbols"]
                    portfolio_weights = st.session_state["portfolio_weights"]
                    
                    # Verificar que todos los símbolos de la cartera estén en los datos
                    available_symbols = set(prices_dict.keys())
                    portfolio_symbols_set = set(portfolio_symbols)
                    
                    if portfolio_symbols_set.issubset(available_symbols):
                        # Filtrar solo los símbolos disponibles y reajustar pesos
                        symbols_in_data = [s for s in portfolio_symbols if s in available_symbols]
                        if len(symbols_in_data) == len(portfolio_symbols):
                            # Todos los símbolos están disponibles
                            symbols = portfolio_symbols
                            weights = portfolio_weights
                            st.info(f"💼 Usando cartera configurada con {len(symbols)} activos")
                        else:
                            # Algunos símbolos faltan, reajustar pesos
                            missing = set(portfolio_symbols) - available_symbols
                            st.warning(f"⚠️ Algunos activos configurados no están en los datos: {missing}. Ajustando pesos...")
                            # Filtrar símbolos y renormalizar pesos
                            symbol_to_weight = dict(zip(portfolio_symbols, portfolio_weights))
                            symbols = symbols_in_data
                            filtered_weights = [symbol_to_weight[s] for s in symbols]
                            # Renormalizar
                            total_weight = sum(filtered_weights)
                            weights = [w / total_weight for w in filtered_weights]
                            st.info(f"📊 Usando {len(symbols)} activos disponibles con pesos ajustados")
                    else:
                        # La cartera configurada no coincide, usar pesos iguales
                        st.warning(f"⚠️ La cartera configurada no coincide con los datos descargados. Usando pesos iguales.")
                        symbols = list(prices_dict.keys())
                        n_assets = len(symbols)
                        weights = [1.0 / n_assets] * n_assets
                        st.info(f"📊 Usando pesos iguales (1/{n_assets} = {1.0/n_assets:.2%} cada uno)")
                else:
                    symbols = list(prices_dict.keys())
                    n_assets = len(symbols)
                    weights = [1.0 / n_assets] * n_assets
                    st.info(f"📊 Usando pesos iguales (1/{n_assets} = {1.0/n_assets:.2%} cada uno)")
                
                portfolio = Portfolio(
                    name="Portfolio",
                    symbols=symbols,
                    weights=weights
                )
                portfolio.set_prices(prices_df)
                
                # Ejecutar simulación
                results = portfolio.monte_carlo_simulation(
                    n_simulations=params.nsims,
                    time_horizon=params.horizonte,
                    initial_value=params.valor_inicial,
                    dynamic_volatility=params.vol_dinamica,
                    random_seed=42
                )
                
                # Guardar resultados en session state
                st.session_state["montecarlo_results"] = results
                st.session_state["montecarlo_portfolio"] = portfolio
                
                st.success(f"✅ Simulación completada exitosamente!")
            
            # Mostrar resultados
            _show_montecarlo_results(results, portfolio)
            
        except Exception as e:
            st.error(f"❌ Error en simulación: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # Mostrar últimos resultados si existen
    elif "montecarlo_results" in st.session_state:
        st.info("Mostrando último resultado de simulación.")
        _show_montecarlo_results(
            st.session_state["montecarlo_results"],
            st.session_state.get("montecarlo_portfolio")
        )
    else:
        st.info("💡 Configura los parámetros de simulación en el panel lateral y ejecuta la simulación.")


def _show_montecarlo_results(results: pd.DataFrame, portfolio: Any) -> None:
    """Muestra los resultados de la simulación Monte Carlo."""
    
    # Estadísticas de la cartera
    if portfolio is not None:
        stats = portfolio.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Retorno esperado", f"{stats['return']:.4f}")
        with col2:
            st.metric("Volatilidad", f"{stats['volatility']:.4f}")
        with col3:
            st.metric("Sharpe Ratio", f"{stats['sharpe_ratio']:.4f}")
        with col4:
            st.metric("Activos", len(portfolio.symbols))
        
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
    
    # Gráfico de trayectorias (OPTIMIZADO: reducido de 100 a 50 trayectorias)
    st.subheader("📈 Trayectorias de simulación")
    
    # Mostrar una muestra de trayectorias (reducido para mejor rendimiento)
    sample_size = min(50, len(results))  # Reducido de 100 a 50
    sample_indices = np.random.choice(len(results), sample_size, replace=False)
    sample_results = results.iloc[sample_indices]
    
    st.line_chart(sample_results.T)
    
    st.divider()
    
    # Histograma del valor final
    st.subheader("📊 Distribución del valor final")
    
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
    st.pyplot(fig)
    
    st.divider()
    
    # Tabla de resumen
    st.subheader("📋 Resumen de simulación")
    st.dataframe(results.describe())

