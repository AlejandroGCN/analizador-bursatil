"""
Monte Carlo Report Generator for portfolio analysis.
"""
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Any
import traceback
import pandas as pd
import hashlib


class MonteCarloReporter:
    """Generador de reportes con análisis Monte Carlo."""
    
    @staticmethod
    def show_montecarlo_summary() -> None:
        """
        Muestra un resumen del análisis Monte Carlo si está disponible.
        """
        if "montecarlo_results" in st.session_state and "montecarlo_portfolio" in st.session_state:
            st.subheader("🎲 Análisis Monte Carlo")
            results = st.session_state["montecarlo_results"]
            
            col1, col2, col3 = st.columns(3)
            final_values = results.iloc[:, -1]
            
            with col1:
                st.metric("💰 Valor medio esperado", f"${final_values.mean():,.2f}")
            with col2:
                st.metric("📊 Percentil 5%", f"${final_values.quantile(0.05):,.2f}")
            with col3:
                st.metric("📈 Percentil 95%", f"${final_values.quantile(0.95):,.2f}")
            
            st.info("💡 Estos valores provienen de una simulación Monte Carlo. Consulta la pestaña '🎲 Monte Carlo' para ver visualizaciones y análisis más detallados.")
            st.divider()
        else:
            st.info("💡 No hay simulaciones Monte Carlo disponibles. El reporte a continuación se basa únicamente en análisis estadístico de datos históricos.")
            st.divider()
    
    @staticmethod
    @st.cache_data(ttl=300, show_spinner=False)
    def _generate_report_markdown_cache(
        symbols_tuple: tuple, 
        weights_tuple: tuple, 
        prices_dict: dict
    ) -> str:
        """
        Genera el reporte markdown de forma cacheada.
        
        Args:
            symbols_tuple: Tupla de símbolos de la cartera
            weights_tuple: Tupla de pesos de la cartera
            prices_dict: Diccionario de precios (serializable)
        
        Returns:
            Reporte en formato markdown
        """
        from simulation import Portfolio
        
        portfolio = Portfolio(
            name="Mi Cartera",
            symbols=list(symbols_tuple),
            weights=list(weights_tuple)
        )
        portfolio.set_prices(pd.DataFrame(prices_dict))
        
        return portfolio.report(risk_free_rate=0.02, include_warnings=True)
    
    @staticmethod
    @st.cache_data(ttl=300, show_spinner=False)
    def _generate_portfolio_plots_cache(
        symbols_tuple: tuple, 
        weights_tuple: tuple, 
        prices_dict: dict
    ) -> bytes:
        """
        Genera los gráficos de la cartera de forma cacheada.
        
        Args:
            symbols_tuple: Tupla de símbolos de la cartera
            weights_tuple: Tupla de pesos de la cartera
            prices_dict: Diccionario de precios (serializable)
        
        Returns:
            Bytes de la imagen PNG
        """
        from simulation import Portfolio
        
        portfolio = Portfolio(
            name="Mi Cartera",
            symbols=list(symbols_tuple),
            weights=list(weights_tuple)
        )
        portfolio.set_prices(pd.DataFrame(prices_dict))
        
        plt.close('all')
        fig = portfolio.plots_report(figsize=(16, 10), save_path=None, return_figure=True)
        
        if fig is None:
            plt.close('all')
            return b''
        
        buffer = BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        plt.close(fig)
        plt.close('all')
        
        return buffer.getvalue()
    
    @staticmethod
    def show_portfolio_report(portfolio: Any) -> None:
        """
        Muestra el reporte completo de la cartera (optimizado con cache).
        
        Args:
            portfolio: Objeto Portfolio con los datos de la cartera
        """
        st.divider()
        
        # Mostrar resumen Monte Carlo si existe
        MonteCarloReporter.show_montecarlo_summary()
        
        # Obtener precios para cache
        data_map = st.session_state.get("last_data_map", {})
        from ui.views.montecarlo_view import _get_prices_from_data_map
        prices_dict = _get_prices_from_data_map(data_map)
        
        # Convertir DataFrame a dict serializable para cache
        prices_df = pd.DataFrame(prices_dict)
        prices_dict_serializable = prices_df.to_dict()
        
        symbols_tuple = tuple(portfolio.symbols)
        weights_tuple = tuple(portfolio.weights)
        
        # Generar reporte en markdown (cacheado)
        st.subheader("📄 Reporte en Markdown")
        report_md = MonteCarloReporter._generate_report_markdown_cache(
            symbols_tuple, weights_tuple, prices_dict_serializable
        )
        
        # Mostrar reporte
        st.markdown(report_md)
        
        st.divider()
        
        # Botón para descargar reporte
        st.download_button(
            label="📥 Descargar reporte en Markdown",
            data=report_md,
            file_name=f"reporte_cartera_{portfolio.name.lower().replace(' ', '_')}.md",
            mime="text/markdown"
        )
        
        st.divider()
        
        # Generar visualizaciones (cacheadas)
        st.subheader("📊 Visualizaciones de la cartera")
        
        try:
            # Generar gráficos de forma cacheada
            plot_bytes = MonteCarloReporter._generate_portfolio_plots_cache(
                symbols_tuple, weights_tuple, prices_dict_serializable
            )
            
            if plot_bytes:
                # Mostrar imagen desde bytes cacheados
                st.image(plot_bytes, width='stretch')
                
                st.divider()
                
                # Botón para descargar visualizaciones
                st.download_button(
                    label="📥 Descargar gráficos (PNG)",
                    data=plot_bytes,
                    file_name=f"visualizaciones_cartera_{portfolio.name.lower().replace(' ', '_')}.png",
                    mime="image/png"
                )
            else:
                st.error("No se pudo generar la figura.")
            
        except Exception as e:
            st.error(f"Error generando visualizaciones: {e}")
            st.code(traceback.format_exc())
        finally:
            # Asegurar que todas las figuras se cierren
            plt.close('all')
